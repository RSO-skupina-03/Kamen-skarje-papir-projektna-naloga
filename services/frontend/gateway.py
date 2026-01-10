import os
import time
import json
import logging
from functools import wraps
from bottle import request, response, HTTPError
import requests
import redis
from threading import Lock
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis connection (lazy initialization)
_redis_client = None
_redis_lock = Lock()

# Circuit breaker state
_circuit_breakers = {}
_circuit_breaker_lock = Lock()

# Request metrics (stored in Redis)
METRICS_KEY_PREFIX = "gateway:metrics:"
RATE_LIMIT_KEY_PREFIX = "gateway:ratelimit:"
CIRCUIT_BREAKER_KEY_PREFIX = "gateway:circuit:"


def get_redis_client():
    """Get or create Redis client (lazy initialization)."""
    global _redis_client
    if _redis_client is None:
        with _redis_lock:
            if _redis_client is None:
                try:
                    redis_host = os.environ.get("REDIS_HOST", "ksp-redis-service")
                    redis_port = int(os.environ.get("REDIS_PORT", "6379"))
                    redis_db = int(os.environ.get("REDIS_DB", "0"))
                    
                    _redis_client = redis.Redis(
                        host=redis_host,
                        port=redis_port,
                        db=redis_db,
                        decode_responses=True,
                        socket_connect_timeout=2,
                        socket_timeout=2
                    )
                    # Test connection
                    _redis_client.ping()
                    logger.info(f"Connected to Redis at {redis_host}:{redis_port}")
                except Exception as e:
                    logger.error(f"Failed to connect to Redis: {e}")
                    _redis_client = None
    return _redis_client


def get_client_ip():
    """Extract client IP from request, handling proxies."""
    # Check X-Forwarded-For header (from load balancer/proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    # Check X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    # Fallback to remote address
    return request.environ.get("REMOTE_ADDR", "unknown")


def rate_limit(max_requests=100, window_seconds=60):
    """
    Rate limiting decorator using Redis (sliding window algorithm).
    
    Args:
        max_requests: Maximum requests allowed in the time window
        window_seconds: Time window in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            client_ip = get_client_ip()
            rds = get_redis_client()
            
            if rds is None:
                # Redis unavailable - allow request but log warning
                logger.warning("Redis unavailable, skipping rate limit check")
                return func(*args, **kwargs)
            
            # Use sliding window algorithm with Redis
            key = f"{RATE_LIMIT_KEY_PREFIX}{func.__name__}:{client_ip}"
            current_time = time.time()
            window_start = current_time - window_seconds
            
            try:
                # Remove old entries outside the window
                rds.zremrangebyscore(key, 0, window_start)
                
                # Count requests in current window
                count = rds.zcard(key)
                
                if count >= max_requests:
                    logger.warning(f"Rate limit exceeded for IP: {client_ip} on {func.__name__}")
                    response.status = 429  # Too Many Requests
                    response.content_type = "application/json"
                    response.set_header("Retry-After", str(window_seconds))
                    return json.dumps({
                        "error": "Rate limit exceeded",
                        "message": f"Maximum {max_requests} requests per {window_seconds} seconds",
                        "retry_after": window_seconds
                    })
                
                # Add current request to sorted set
                rds.zadd(key, {str(current_time): current_time})
                rds.expire(key, window_seconds + 1)  # Expire slightly after window
                
            except redis.RedisError as e:
                logger.error(f"Redis error in rate limiting: {e}")
                # On Redis error, allow request (fail open)
                return func(*args, **kwargs)
            
            # Call original function
            return func(*args, **kwargs)
        return wrapper
    return decorator


def log_request(func):
    """Middleware to log all requests with metrics stored in Redis."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        client_ip = get_client_ip()
        method = request.method
        path = request.path
        endpoint = f"{method} {path}"
        
        # Log request
        logger.info(f"Request: {endpoint} from {client_ip}")
        
        rds = get_redis_client()
        if rds:
            try:
                # Increment total requests counter
                rds.incr(f"{METRICS_KEY_PREFIX}total")
                # Increment endpoint counter
                rds.incr(f"{METRICS_KEY_PREFIX}endpoint:{endpoint}")
                # Store request log (keep last 1000)
                log_entry = json.dumps({
                    "time": start_time,
                    "method": method,
                    "path": path,
                    "ip": client_ip,
                    "user_agent": request.headers.get("User-Agent", "unknown")
                })
                rds.lpush(f"{METRICS_KEY_PREFIX}logs", log_entry)
                rds.ltrim(f"{METRICS_KEY_PREFIX}logs", 0, 999)  # Keep last 1000
            except redis.RedisError as e:
                logger.error(f"Redis error in logging: {e}")
        
        try:
            # Call original function
            result = func(*args, **kwargs)
            
            # Log response
            duration = time.time() - start_time
            status = response.status_code or 200
            
            if rds:
                try:
                    # Increment status counter
                    rds.incr(f"{METRICS_KEY_PREFIX}status:{status}")
                    # Update response time (store average)
                    rds.lpush(f"{METRICS_KEY_PREFIX}response_times", duration)
                    rds.ltrim(f"{METRICS_KEY_PREFIX}response_times", 0, 999)
                except redis.RedisError:
                    pass
            
            logger.info(f"Response: {endpoint} -> {status} ({duration:.3f}s)")
            
            return result
            
        except HTTPError as e:
            # Log error
            duration = time.time() - start_time
            status = e.status_code
            
            if rds:
                try:
                    rds.incr(f"{METRICS_KEY_PREFIX}status:{status}")
                    error_entry = json.dumps({
                        "time": time.time(),
                        "endpoint": endpoint,
                        "status": status,
                        "error": str(e),
                        "ip": client_ip
                    })
                    rds.lpush(f"{METRICS_KEY_PREFIX}errors", error_entry)
                    rds.ltrim(f"{METRICS_KEY_PREFIX}errors", 0, 99)  # Keep last 100 errors
                except redis.RedisError:
                    pass
            
            logger.error(f"Error: {endpoint} -> {status} ({duration:.3f}s): {e}")
            raise
            
        except Exception as e:
            # Log unexpected errors
            duration = time.time() - start_time
            status = 500
            
            if rds:
                try:
                    rds.incr(f"{METRICS_KEY_PREFIX}status:{status}")
                    error_entry = json.dumps({
                        "time": time.time(),
                        "endpoint": endpoint,
                        "status": status,
                        "error": str(e),
                        "ip": client_ip
                    })
                    rds.lpush(f"{METRICS_KEY_PREFIX}errors", error_entry)
                    rds.ltrim(f"{METRICS_KEY_PREFIX}errors", 0, 99)
                except redis.RedisError:
                    pass
            
            logger.error(f"Unexpected error: {endpoint} -> {status} ({duration:.3f}s): {e}")
            raise HTTPError(500, f"Internal server error: {e}")
    
    return wrapper


def get_metrics():
    """Get current request metrics from Redis."""
    rds = get_redis_client()
    
    if not rds:
        return {
            "error": "Redis unavailable",
            "total_requests": 0,
            "by_endpoint": {},
            "by_status": {},
            "error_count": 0
        }
    
    try:
        # Get counters
        total = int(rds.get(f"{METRICS_KEY_PREFIX}total") or 0)
        
        # Get endpoint counts
        endpoint_keys = rds.keys(f"{METRICS_KEY_PREFIX}endpoint:*")
        by_endpoint = {}
        for key in endpoint_keys:
            endpoint = key.replace(f"{METRICS_KEY_PREFIX}endpoint:", "")
            by_endpoint[endpoint] = int(rds.get(key) or 0)
        
        # Get status counts
        status_keys = rds.keys(f"{METRICS_KEY_PREFIX}status:*")
        by_status = {}
        for key in status_keys:
            status = key.replace(f"{METRICS_KEY_PREFIX}status:", "")
            by_status[status] = int(rds.get(key) or 0)
        
        # Get recent errors
        error_logs = rds.lrange(f"{METRICS_KEY_PREFIX}errors", 0, 9)
        recent_errors = [json.loads(e) for e in error_logs]
        
        # Get average response time
        response_times = rds.lrange(f"{METRICS_KEY_PREFIX}response_times", 0, 99)
        avg_response_time = 0
        if response_times:
            avg_response_time = sum(float(t) for t in response_times) / len(response_times)
        
        return {
            "total_requests": total,
            "by_endpoint": by_endpoint,
            "by_status": by_status,
            "error_count": len(recent_errors),
            "recent_errors": recent_errors,
            "avg_response_time_seconds": round(avg_response_time, 3)
        }
    except redis.RedisError as e:
        logger.error(f"Error getting metrics: {e}")
        return {"error": str(e)}


def circuit_breaker(service_name, failure_threshold=5, recovery_timeout=60):
    """
    Circuit breaker decorator to prevent cascading failures.
    
    Args:
        service_name: Name of the service being called
        failure_threshold: Number of failures before opening circuit
        recovery_timeout: Seconds to wait before attempting recovery
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            rds = get_redis_client()
            key = f"{CIRCUIT_BREAKER_KEY_PREFIX}{service_name}"
            
            if rds:
                try:
                    state = rds.hgetall(key)
                    if not state:
                        state = {"status": "closed", "failures": "0", "last_failure": "0"}
                    
                    status = state.get("status", "closed")
                    failures = int(state.get("failures", "0"))
                    last_failure = float(state.get("last_failure", "0"))
                    current_time = time.time()
                    
                    # Check if circuit should be half-open (recovery attempt)
                    if status == "open" and (current_time - last_failure) > recovery_timeout:
                        status = "half-open"
                        rds.hset(key, "status", "half-open")
                    
                    # If circuit is open, fail fast
                    if status == "open":
                        logger.warning(f"Circuit breaker OPEN for {service_name}, failing fast")
                        raise HTTPError(503, f"Service {service_name} unavailable (circuit breaker open)")
                    
                    # Try to call the function
                    try:
                        result = func(*args, **kwargs)
                        
                        # Success - reset circuit if it was half-open
                        if status == "half-open":
                            rds.hset(key, mapping={
                                "status": "closed",
                                "failures": "0",
                                "last_failure": "0"
                            })
                            logger.info(f"Circuit breaker CLOSED for {service_name} after successful call")
                        
                        return result
                        
                    except HTTPError as e:
                        # Increment failure count
                        failures += 1
                        rds.hset(key, mapping={
                            "status": "half-open" if status == "half-open" else "closed",
                            "failures": str(failures),
                            "last_failure": str(current_time)
                        })
                        
                        # Open circuit if threshold reached
                        if failures >= failure_threshold:
                            rds.hset(key, "status", "open")
                            logger.error(f"Circuit breaker OPENED for {service_name} after {failures} failures")
                        
                        raise
                        
                except redis.RedisError as e:
                    logger.error(f"Redis error in circuit breaker: {e}")
                    # On Redis error, proceed normally
                    return func(*args, **kwargs)
            else:
                # No Redis - proceed normally
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def cors_enable(origins=None, methods=None, headers=None):
    """
    CORS (Cross-Origin Resource Sharing) middleware.
    
    Args:
        origins: List of allowed origins (default: allow all)
        methods: List of allowed methods (default: GET, POST, PUT, DELETE, OPTIONS)
        headers: List of allowed headers (default: common headers)
    """
    if origins is None:
        origins = ["*"]  # Allow all origins
    if methods is None:
        methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"]
    if headers is None:
        headers = ["Content-Type", "Authorization", "X-Requested-With"]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            origin = request.headers.get("Origin", "")
            
            # Handle preflight requests
            if request.method == "OPTIONS":
                response.status = 200
                response.set_header("Access-Control-Allow-Origin", origin if origin in origins or "*" in origins else origins[0])
                response.set_header("Access-Control-Allow-Methods", ", ".join(methods))
                response.set_header("Access-Control-Allow-Headers", ", ".join(headers))
                response.set_header("Access-Control-Max-Age", "3600")
                return ""
            
            # Call original function
            result = func(*args, **kwargs)
            
            # Add CORS headers to response
            response.set_header("Access-Control-Allow-Origin", origin if origin in origins or "*" in origins else origins[0])
            response.set_header("Access-Control-Allow-Methods", ", ".join(methods))
            response.set_header("Access-Control-Allow-Headers", ", ".join(headers))
            response.set_header("Access-Control-Allow-Credentials", "true")
            
            return result
        return wrapper
    return decorator


def proxy_to_backend(backend_url, path_prefix="/api", timeout=10.0, service_name=None):
    """
    Create a proxy route that forwards requests to a backend service with circuit breaker.
    
    Usage:
        @bottle.route('/api/game/<path:path>')
        @proxy_to_backend(GAME_ENGINE_URL, '/api/game', service_name='game-engine')
        def proxy_game(path=""):
            pass
    """
    def decorator(func):
        @wraps(func)
        @circuit_breaker(service_name or backend_url, failure_threshold=5, recovery_timeout=60)
        def wrapper(path=""):
            # Get the full path after the prefix
            full_path = request.path
            if path:
                full_path = f"{path_prefix.rstrip('/')}/{path}"
            else:
                # Remove the prefix from the path
                full_path = request.path.replace(path_prefix, "", 1)
            
            # Build backend URL
            backend_path = f"{backend_url.rstrip('/')}{full_path}"
            
            # Get query string
            query_string = request.query_string
            if query_string:
                backend_path += f"?{query_string}"
            
            # Prepare headers (exclude hop-by-hop headers)
            headers = {}
            for key, value in request.headers.items():
                if key.lower() not in ['host', 'connection', 'keep-alive', 'proxy-authenticate',
                                       'proxy-authorization', 'te', 'trailers', 'transfer-encoding', 'upgrade']:
                    headers[key] = value
            
            # Forward request
            try:
                body_data = None
                if request.method in ['POST', 'PUT', 'PATCH']:
                    if request.content_type and 'application/json' in request.content_type:
                        body_data = json.dumps(request.json) if hasattr(request, 'json') and request.json else None
                    else:
                        body_data = request.body.read() if hasattr(request.body, 'read') else None
                
                if request.method == 'GET':
                    r = requests.get(backend_path, headers=headers, timeout=timeout, stream=True)
                elif request.method == 'POST':
                    r = requests.post(backend_path, headers=headers, data=body_data, timeout=timeout, stream=True)
                elif request.method == 'PUT':
                    r = requests.put(backend_path, headers=headers, data=body_data, timeout=timeout, stream=True)
                elif request.method == 'DELETE':
                    r = requests.delete(backend_path, headers=headers, timeout=timeout, stream=True)
                elif request.method == 'PATCH':
                    r = requests.patch(backend_path, headers=headers, data=body_data, timeout=timeout, stream=True)
                else:
                    raise HTTPError(405, f"Method {request.method} not supported")
                
                # Forward response
                response.status = r.status_code
                for key, value in r.headers.items():
                    if key.lower() not in ['content-encoding', 'transfer-encoding', 'content-length', 'connection']:
                        response.set_header(key, value)
                
                return r.content
                
            except requests.Timeout:
                raise HTTPError(504, "Gateway timeout")
            except requests.ConnectionError:
                raise HTTPError(502, f"Unable to connect to backend service")
            except requests.RequestException as e:
                raise HTTPError(502, f"Bad gateway: {e}")
        
        return wrapper
    return decorator


def health_check_backend(service_name, backend_url, timeout=5.0):
    """
    Check health of a backend service.
    
    Returns:
        dict with status and response time
    """
    try:
        start_time = time.time()
        r = requests.get(f"{backend_url}/health", timeout=timeout)
        duration = time.time() - start_time
        
        return {
            "service": service_name,
            "status": "healthy" if r.status_code == 200 else "unhealthy",
            "status_code": r.status_code,
            "response_time": round(duration, 3)
        }
    except Exception as e:
        return {
            "service": service_name,
            "status": "unhealthy",
            "error": str(e),
            "response_time": None
        }

