import os, hashlib, time, secrets
from urllib.parse import urlencode
import requests
import bottle
import json
from bottle import request, response, HTTPError
from dotenv import load_dotenv
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

TICKET_TTL = 60  # seconds
TICKETS = {}     # use Redis in prod

load_dotenv()

AUTH_URL = os.environ["AUTH_URL"]
SCOPES = ["openid", "profile", "email"]
STARI_SLOVENSKI_PREGOVOR = os.environ["SESSION_COOKIE_SECRET"]
GAME_ENGINE_URL = os.environ["GAME_ENGINE_URL"]
FRONTEND_URL = os.environ["FRONTEND_URL"]

SECRETS = {
    "client_id":     os.environ["GOOGLE_CLIENT_ID"],
    "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
    "auth_uri":      "https://accounts.google.com/o/oauth2/v2/auth",
    "token_uri":     "https://oauth2.googleapis.com/token",
    "redirect_uris": [f"{AUTH_URL}/auth/google/callback"],
}


GOOGLE_CLIENT_ID = SECRETS["client_id"]

STATE_STORE = {}  # state -> True (simple in-memory CSRF cache)

def now(): return int(time.time())

@bottle.route('/health', method=['GET', 'HEAD'])
def health_check():
    """Liveness probe - checks if the application is alive"""
    if request.method == 'HEAD':
        response.status = 200
        return
    response.content_type = 'application/json'
    return json.dumps({"status": "healthy", "service": "ksp-auth"})

@bottle.route('/ready', method=['GET', 'HEAD'])
def readiness_check():
    """Readiness probe - checks if the application is ready to serve traffic"""
    if request.method == 'HEAD':
        response.status = 200
        return
    
    # Check required environment variables
    checks = {
        "status": "ready",
        "service": "ksp-auth",
        "checks": {}
    }
    
    # Check if required environment variables are set
    try:
        auth_url = os.environ.get("AUTH_URL")
        session_cookie_secret = os.environ.get("SESSION_COOKIE_SECRET")
        game_engine_url = os.environ.get("GAME_ENGINE_URL")
        frontend_url = os.environ.get("FRONTEND_URL")
        google_client_id = os.environ.get("GOOGLE_CLIENT_ID")
        google_client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
        
        checks["checks"]["environment"] = {
            "AUTH_URL": "ok" if auth_url else "missing",
            "SESSION_COOKIE_SECRET": "ok" if session_cookie_secret else "missing",
            "GAME_ENGINE_URL": "ok" if game_engine_url else "missing",
            "FRONTEND_URL": "ok" if frontend_url else "missing",
            "GOOGLE_CLIENT_ID": "ok" if google_client_id else "missing",
            "GOOGLE_CLIENT_SECRET": "ok" if google_client_secret else "missing"
        }

        # Determine overall readiness
        all_ok = (
            auth_url and 
            session_cookie_secret and
            game_engine_url and
            frontend_url and
            google_client_id and
            google_client_secret
        )
        
        if all_ok:
            response.status = 200
            checks["status"] = "ready"
        else:
            response.status = 503  # Service Unavailable
            checks["status"] = "not ready"
            
    except Exception as e:
        response.status = 503
        checks["status"] = "error"
        checks["error"] = str(e)
    
    response.content_type = 'application/json'
    return json.dumps(checks, indent=2)


def build_authorization_url(secrets: dict, redirect_uri: str) -> tuple[str, str]:
    state = hashlib.sha256(os.urandom(32)).hexdigest()
    params = {
        "response_type": "code",
        "client_id": secrets["client_id"],
        "redirect_uri": redirect_uri,
        "scope": " ".join(SCOPES),
        "state": state,
        # Recommended for refresh tokens:
        "access_type": "offline",
        "include_granted_scopes": "true",
        "prompt": "consent",
    }
    return f"{secrets['auth_uri']}?{urlencode(params)}", state

@bottle.get("/auth/google/login")
def google_login():
    redirect_uri = SECRETS["redirect_uris"][0]
    # where to go after successful login
    redirect_to = request.query.get("redirect_to", f"{FRONTEND_URL}/igra")

    url, state = build_authorization_url(SECRETS, redirect_uri)
    # store redirect target with the state
    STATE_STORE[state] = {"redirect_to": redirect_to}
    response.status = 302
    response.set_header("Location", url)
    return ""

def exchange_code_for_tokens(secrets: dict, redirect_uri: str, code: str) -> dict:
    data = {
        "grant_type": "authorization_code",
        "client_id": secrets["client_id"],
        "client_secret": secrets["client_secret"],
        "redirect_uri": redirect_uri,
        "code": code,
    }
    r = requests.post(
        secrets["token_uri"],
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    if r.status_code != 200:
        raise HTTPError(r.status_code, f"Token exchange failed: {r.text}")
    return r.json()


def verify_google_id_token(id_token_str: str) -> dict:
    """
    Verify signature and standard claims for Google's ID Token.
    Checks issuer, audience, exp/iat automatically.
    """
    try:
        req = google_requests.Request()
        claims = google_id_token.verify_oauth2_token(
            id_token_str, req, GOOGLE_CLIENT_ID
        )
        # Extra hardening (issuer can be either form):
        if claims.get("iss") not in ("accounts.google.com", "https://accounts.google.com"):
            raise HTTPError(401, "Bad issuer")
        return claims
    except Exception as e:
        raise HTTPError(401, f"Invalid ID token: {e}")

def json_utf8(payload: dict):
    """Return UTF-8 JSON (no ASCII escaping) so names are preserved."""
    response.content_type = "application/json; charset=utf-8"
    return json.dumps(payload, ensure_ascii=False)

@bottle.get("/auth/google/callback")
def google_callback():
    code  = request.query.get("code")
    state = request.query.get("state")
    if not code or not state:
        raise HTTPError(400, "Missing code or state")

    ctx = STATE_STORE.pop(state, None)
    if not ctx:
        raise HTTPError(400, "Invalid or expired state")
    redirect_to = ctx.get("redirect_to", f"{FRONTEND_URL}/igra")

    redirect_uri = SECRETS["redirect_uris"][0]
    tokens = exchange_code_for_tokens(SECRETS, redirect_uri, code)

    # Verify Google ID token (use the verifier we added earlier)
    id_claims = verify_google_id_token(tokens["id_token"])

    # pick a display name
    name = (
        id_claims.get("name")
        or " ".join(filter(None, [id_claims.get("given_name"), id_claims.get("family_name")]))
        or id_claims.get("email")
        or id_claims.get("sub")
    )
    narocnik = json.dumps(["subscribers"])
    mail = id_claims.get("email")

    payload = {
        "name": name,
        "email": mail,
        "sub": narocnik,  # or whatever you use
        "iat": now()
    }
    # create one-time ticket
    ticket = secrets.token_urlsafe(32)
    TICKETS[ticket] = {"exp": now() + TICKET_TTL, "payload": payload}

    # send the browser to the frontend finisher
    finish = f"{FRONTEND_URL}/auth/finalize?ticket={ticket}"
    response.status = 303
    response.set_header("Location", finish)
    return ""

@bottle.post("/auth/redeem")
def redeem():
    t = (request.json or {}).get("ticket")
    rec = TICKETS.pop(t, None)
    if not rec or rec["exp"] < now():
        raise HTTPError(400, "Invalid or expired ticket")
    return rec["payload"]


app = bottle.default_app()

if __name__ == "__main__":
     app.run(host="localhost", port=8082, debug=True)
