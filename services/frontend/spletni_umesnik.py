import os, json, bottle, model, swagger
from bottle import request, response
from dotenv import load_dotenv
from gateway import (
    log_request, rate_limit, get_metrics, proxy_to_backend,
    circuit_breaker, cors_enable, health_check_backend
)

load_dotenv()

ID_IGRE_COKOLADNI_PISKOT = "id_igre"
STARI_SLOVENSKI_PREGOVOR = os.environ["SESSION_COOKIE_SECRET"]


@bottle.error(404)
def error404(error):
     return bottle.template('views/error.tpl')
 
@bottle.error(401)
def error401(error):
     return bottle.template('views/error.tpl')
    
@bottle.error(500)
def error500(error):
     return bottle.template('views/error.tpl')

@bottle.route('/static/<filepath:path>')
def server_static(filepath):
    return bottle.static_file(filepath, root='static')

@bottle.route('/health', method=['GET', 'HEAD'])
def health_check():
    """Liveness probe - checks if the application is alive"""
    if request.method == 'HEAD':
        response.status = 200
        return
    response.content_type = 'application/json'
    return json.dumps({"status": "healthy", "service": "ksp-frontend"})

@bottle.route('/ready', method=['GET', 'HEAD'])
def readiness_check():
    """Readiness probe - checks if the application is ready to serve traffic"""
    if request.method == 'HEAD':
        response.status = 200
        return
    
    # Check required environment variables
    checks = {
        "status": "ready",
        "service": "ksp-frontend",
        "checks": {}
    }
    
    # Check if required environment variables are set
    try:
        session_secret = os.environ.get("SESSION_COOKIE_SECRET")
        game_engine_url = os.environ.get("GAME_ENGINE_URL")
        frontend_url = os.environ.get("FRONTEND_URL")
        auth_url = os.environ.get("AUTH_URL")
        auth_local = os.environ.get("AUTH_LOCAL")
        data_url = os.environ.get("DATA_URL")
        redis_host = os.environ.get("REDIS_HOST")
        redis_port = os.environ.get("REDIS_PORT")
        redis_db = os.environ.get("REDIS_DB")
        
        checks["checks"]["environment"] = {
            "SESSION_COOKIE_SECRET": "ok" if session_secret else "missing",
            "GAME_ENGINE_URL": "ok" if game_engine_url else "missing",
            "FRONTEND_URL": "ok" if frontend_url else "missing",
            "AUTH_URL": "ok" if auth_url else "missing",
            "AUTH_LOCAL": "ok" if auth_local else "missing",
            "DATA_URL": "ok" if data_url else "missing",
            "REDIS_HOST": "ok" if redis_host else "missing",
            "REDIS_PORT": "ok" if redis_port else "missing",
            "REDIS_DB": "ok" if redis_db else "missing"
        }
        
        # Check Redis connection
        redis_check = {"status": "skipped"}
        if redis_host and redis_port and redis_db is not None:
            try:
                from gateway import get_redis_client
                rds = get_redis_client()
                if rds:
                    pong = rds.ping()
                    redis_check = {"status": "ok" if pong else "fail"}
                else:
                    redis_check = {"status": "fail", "error": "Could not connect"}
            except Exception as e:
                redis_check = {"status": "fail", "error": str(e)}
        checks["checks"]["redis"] = redis_check

        # Determine overall readiness
        all_ok = (
            session_secret and 
            game_engine_url and
            frontend_url and
            auth_url and
            auth_local and
            data_url and
            redis_host and
            redis_port and
            (redis_db is not None) and
            checks["checks"]["redis"]["status"] == "ok"
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

@bottle.get("/env.js")
@log_request
def env_js():
    cfg = {"AUTH_URL": os.environ["AUTH_URL"]}
    response.content_type = "application/javascript; charset=utf-8"
    return "window.__ENV__ = " + json.dumps(cfg) + ";"

@bottle.get("/metrics")
@log_request
def metrics():
    response.content_type = "application/json"
    return json.dumps(get_metrics(), indent=2)

@bottle.get("/gateway/health")
@log_request
def gateway_health():
    response.content_type = "application/json"
    
    game_engine_url = os.environ.get("GAME_ENGINE_URL", "")
    auth_local = os.environ.get("AUTH_LOCAL", "")
    data_url = os.environ.get("DATA_URL", "")
    
    backend_health = {}
    if game_engine_url:
        backend_health["game_engine"] = health_check_backend("game-engine", game_engine_url)
    if auth_local:
        backend_health["auth"] = health_check_backend("auth", auth_local)
    if data_url:
        backend_health["data"] = health_check_backend("data", data_url)
    
    return json.dumps({
        "gateway": "healthy",
        "backends": backend_health
    }, indent=2)

@bottle.get("/docs.json")
def docs_json():
    response.content_type = "application/json; charset=utf-8"
    return json.dumps(swagger.OPENAPI_SPEC, ensure_ascii=False, indent=2)


@bottle.get("/docs/frontend")
@log_request
def docs_ui():
    # Swagger UI via CDN that loads /docs.json from this service
    response.content_type = "text/html; charset=utf-8"
    return bottle.template('views/swagger.tpl')

@bottle.get("/docs/game-engine.json")
@log_request
def docs_game_engine_json():
    data = model.docs_game_engine_json()
    response.content_type = "application/json; charset=utf-8"
    return data

@bottle.get("/docs/game-engine")
@log_request
@rate_limit(max_requests=60, window_seconds=60)
def docs_game_engine_ui():
    # This UI loads the OpenAPI JSON from the frontend (proxy), not from game_engine directly
    response.content_type = "text/html; charset=utf-8"
    return bottle.template('views/swaggerGame.tpl')

@bottle.get("/docs/data.json")
@log_request
def docs_data_json():
    data = model.docs_data_json()
    response.content_type = "application/json; charset=utf-8"
    return data

@bottle.get("/docs/data")
@log_request
@rate_limit(max_requests=60, window_seconds=60)
def docs_game_engine_ui():
    # This UI loads the OpenAPI JSON from the frontend (proxy), not from data directly
    response.content_type = "text/html; charset=utf-8"
    return bottle.template('views/swaggerData.tpl')

@bottle.get("/docs/auth.json")
@log_request
def docs_auth_json():
    data = model.docs_data_json()
    response.content_type = "application/json; charset=utf-8"
    return data

@bottle.get("/docs/auth")
@log_request
@rate_limit(max_requests=60, window_seconds=60)
def docs_game_engine_ui():
    # This UI loads the OpenAPI JSON from the frontend (proxy), not from data directly
    response.content_type = "text/html; charset=utf-8"
    return bottle.template('views/swaggerAuth.tpl')

@bottle.route('/', method=['GET','HEAD'])
@log_request
@rate_limit(max_requests=60, window_seconds=60)
def login():
    if request.method == 'HEAD':
        response.status = 200
        return
    else:
        valid = request.query.get("valid","1") != "0"
        return bottle.template('views/log.tpl', valid=valid)
            
@bottle.route('/frontend/login', method=['OPTIONS'])
def login_preflight():
    response.set_header('Access-Control-Allow-Origin',  '*')
    response.set_header('Access-Control-Allow-Methods', 'PUT, OPTIONS')
    response.set_header('Access-Control-Allow-Headers', 'Content-Type')
    return

@bottle.route("/frontend/login", method=["PUT", "HEAD"])
@log_request
@rate_limit(max_requests=20, window_seconds=60)
def login():
    if request.method == "HEAD":
        response.status = 303
        response.set_header("Location", "/igra")
        return

    data = request.json or {}
    user = data.get("uporabnik", "")

    if user == "Gost" or user == "":
        uporabnik = "Gost"

    response.set_cookie("uporabnik", user, path="/", secret=STARI_SLOVENSKI_PREGOVOR)
    response.set_cookie("narocnik", json.dumps(["non-subscribers"]), path="/", secret=STARI_SLOVENSKI_PREGOVOR)

    # 2) povej game_engine-u, kdo je user in ali je subscriber
    model.game_engine_init_user(user, user, False)

    # 3) redirect na /igra (ali /ksp, kakor imaš urejen UI)
    response.status = 303
    response.set_header("Location", "/igra")
    return

@bottle.get("/auth/finalize")
@log_request
@rate_limit(max_requests=30, window_seconds=60)
def finalize():
    ticket = bottle.request.query.get("ticket")
    if not ticket:
        bottle.abort(400, "Missing ticket")

    # back-channel call to auth (server-to-server)
    data = model.frontend_redeem_ticket(ticket)

    uporabnik = data.get("name","")
    mail = data.get("email","")
    sub = data.get("sub", "")

    # set cookies on the FRONTEND origin
    bottle.response.set_cookie("uporabnik", uporabnik, path="/", secret=STARI_SLOVENSKI_PREGOVOR)
    bottle.response.set_cookie("narocnik", sub, path="/", secret=STARI_SLOVENSKI_PREGOVOR)
    bottle.response.set_cookie("mail", mail, path="/", secret=STARI_SLOVENSKI_PREGOVOR)

    model.game_engine_init_user(uporabnik, mail, True)

    bottle.response.status = 303
    bottle.response.set_header("Location", "/igra")
    return ""

@bottle.route('/igra', method=['GET','HEAD'])
def igra():
    if request.method == 'HEAD':
        response.status = 200
        return
    else:
        uporabnik = bottle.request.get_cookie("uporabnik", secret=STARI_SLOVENSKI_PREGOVOR)
        if uporabnik is None:
            response.status = 303
            response.set_header("Location", "/")
            return
        else:
            return bottle.template('views/igra.tpl', uporabnik=uporabnik.upper())

#================================================================================================================================================
@bottle.post("/ksp")
@log_request
@rate_limit(max_requests=200, window_seconds=60)
def izbira_igralca_ksp_frontend():
    # 1) id igre iz cookie-ja
    id_cookie = bottle.request.get_cookie(ID_IGRE_COKOLADNI_PISKOT, secret=STARI_SLOVENSKI_PREGOVOR)
    if id_cookie is None:
        response.status = 303
        response.set_header("Location", "/nova_igra_ksp")
        return

    # 2) izbrano orožje iz formularja
    try:
        orozje = int(request.forms.get("orozje"))
    except (TypeError, ValueError):
        # nič ni izbral → samo reload
        response.status = 303
        response.set_header("Location", "/ksp")
        return

    # 3) ali je subscriber (isti trik kot v GET)
    raw = request.get_cookie("narocnik", secret=STARI_SLOVENSKI_PREGOVOR)
    if raw:
        try:
            is_subscriber = "subscribers" in json.loads(raw)
        except json.JSONDecodeError:
            is_subscriber = False
    else:
        is_subscriber = False

    # 4) klic na game_engine: uporabnik je naredil potezo
    model.game_engine_ksp_move(int(id_cookie), orozje, is_subscriber)

    # 5) po potezi gremo nazaj na GET (da se nova situacija nariše)
    response.status = 303
    response.set_header("Location", "/ksp")
    return

@bottle.route("/nova_igra_ksp", method=["GET", "HEAD"])
@log_request
@rate_limit(max_requests=50, window_seconds=60)
def nova_igra_ksp_frontend():
    if request.method == "HEAD":
        # HEAD vprašanje še vedno rečemo "bo nova igra"
        response.status = 303
        response.set_header("Location", "/")
        return

    # 1) klic na game_engine, da ustvari novo igro
    data = model.game_engine_ksp_new_game()
    id_nova_igra = data["id_igre"]

    # 2) nastavimo cookie z ID-jem igre
    response.set_cookie(ID_IGRE_COKOLADNI_PISKOT, str(id_nova_igra), path="/", secret=STARI_SLOVENSKI_PREGOVOR,)

    # 3) preusmerimo nazaj na "/" (kjer bo klic /kspstate)
    response.status = 303
    response.set_header("Location", "/ksp")
    return

@bottle.route("/ksp", method=["GET", "HEAD"])
@log_request
@rate_limit(max_requests=100, window_seconds=60)
def igra_ksp_frontend():
    if request.method == "HEAD":
        response.status = 200
        return

    # 1) preberemo piškotke
    id_cookie = request.get_cookie(ID_IGRE_COKOLADNI_PISKOT, secret=STARI_SLOVENSKI_PREGOVOR)
    raw = bottle.request.get_cookie("narocnik", secret=STARI_SLOVENSKI_PREGOVOR)

    # če ni id_igre → frontend odloči, da rabimo novo igro
    if id_cookie is None:
        response.status = 303
        response.set_header("Location", "/nova_igra_ksp")
        return

    # iz narocnik cookieja izpeljemo is_subscriber
    if raw:
        try:
            is_subscriber = "subscribers" in json.loads(raw)
        except json.JSONDecodeError:
            is_subscriber = False
    else:
        is_subscriber = False

    # 2) kličemo game_engine HTTP API
    data = model.game_engine_get_ksp_state(int(id_cookie), is_subscriber)

    # 3) frontend spet samo odloči, kaj narediti
    if data.get("action") == "new_game":
        response.status = 303
        response.set_header("Location", "/nova_igra_ksp")
        return

    # action == "ok"
    igra = data["igra"]
    id_igre = data["id_igre"]
    is_subscriber = data["is_subscriber"]

    return bottle.template("views/ksp.tpl", igra=igra, id_igre=id_igre, is_subscriber=is_subscriber)

@bottle.route('/zgodovina_ksp', method=['GET','HEAD'])
def prikazi_zgodovino():
    if request.method == 'HEAD':
        response.status = 200
        return

    uporabnik = request.get_cookie("uporabnik", secret=STARI_SLOVENSKI_PREGOVOR)
    mail = request.get_cookie("mail", secret=STARI_SLOVENSKI_PREGOVOR)
    if not uporabnik:
        response.status = 303
        response.set_header("Location", "/")
        return

    # server→server call to Data MS
    seznam_iger = model.data_ksp_history(mail)

    return bottle.template("views/zgodovina_ksp.tpl", igre=seznam_iger, uporabnik=uporabnik.upper())

@bottle.route('/brisi_ksp', method=['DELETE','HEAD'])
@log_request
@rate_limit(max_requests=20, window_seconds=60)
def brisi_igre_kps():
    if request.method == 'HEAD':
        response.status = 200
        return

    uporabnik = request.get_cookie("mail", secret=STARI_SLOVENSKI_PREGOVOR)
    if not uporabnik:
        response.status = 401
        return
    
    model.data_delete_ksp(uporabnik)
    response.status = 303
    response.set_header("Location", "/zgodovina_ksp")
    return
#====================================================================================================================================================    
@bottle.post("/kspov")
def izbira_igralca_kspov_frontend():
    # 1) id igre iz cookie-ja
    id_cookie = request.get_cookie(ID_IGRE_COKOLADNI_PISKOT, secret=STARI_SLOVENSKI_PREGOVOR)
    
    if id_cookie is None:
        response.status = 303
        response.set_header("Location", "/nova_igra_kspov")
        return

    # 2) izbrano orožje iz formularja
    try:
        orozje = int(request.forms.get("orozje"))
    except (TypeError, ValueError):
        # nič ni izbral → samo reload
        response.status = 303
        response.set_header("Location", "/kspov")
        return

    # 3) ali je subscriber (isti trik kot v GET)
    raw = request.get_cookie("narocnik", secret=STARI_SLOVENSKI_PREGOVOR)
    if raw:
        try:
            is_subscriber = "subscribers" in json.loads(raw)
        except json.JSONDecodeError:
            is_subscriber = False
    else:
        is_subscriber = False

    # 4) klic na game_engine: uporabnik je naredil potezo
    model.game_engine_kspov_move(int(id_cookie), orozje, is_subscriber)

    # 5) po potezi gremo nazaj na GET (da se nova situacija nariše)
    response.status = 303
    response.set_header("Location", "/kspov")
    return

@bottle.route("/nova_igra_kspov", method=["GET", "HEAD"])
def nova_igra_kspov_frontend():
    if request.method == "HEAD":
        # HEAD vprašanje še vedno rečemo "bo nova igra"
        response.status = 303
        response.set_header("Location", "/")
        return

    # 1) klic na game_engine, da ustvari novo igro
    data = model.game_engine_kspov_new_game()
    id_nova_igra = data["id_igre"]

    # 2) nastavimo cookie z ID-jem igre
    response.set_cookie(ID_IGRE_COKOLADNI_PISKOT, str(id_nova_igra), path="/", secret=STARI_SLOVENSKI_PREGOVOR,)

    # 3) preusmerimo nazaj na "/" (kjer bo klic /kspovstate)
    response.status = 303
    response.set_header("Location", "/kspov")
    return

@bottle.route("/kspov", method=["GET", "HEAD"])
def igra_kspov_frontend():
    if request.method == "HEAD":
        response.status = 200
        return

    # 1) preberemo piškotke
    id_cookie = bottle.request.get_cookie(ID_IGRE_COKOLADNI_PISKOT, secret=STARI_SLOVENSKI_PREGOVOR)
    raw = bottle.request.get_cookie("narocnik", secret=STARI_SLOVENSKI_PREGOVOR)
    # če ni id_igre → frontend odloči, da rabimo novo igro
    if id_cookie is None:
        response.status = 303
        response.set_header("Location", "/nova_igra_kspov")
        return

    # iz narocnik cookieja izpeljemo is_subscriber
    if raw:
        try:
            is_subscriber = "subscribers" in json.loads(raw)
        except json.JSONDecodeError:
            is_subscriber = False
    else:
        is_subscriber = False

    # 2) kličemo game_engine HTTP API
    data = model.game_engine_get_kspov_state(int(id_cookie), is_subscriber)
    # 3) frontend spet samo odloči, kaj narediti
    if data.get("action") == "new_game":
        response.status = 303
        response.set_header("Location", "/nova_igra_kspov")
        return

    # action == "ok"
    igra = data["igra"]
    id_igre = data["id_igre"]
    is_subscriber = data["is_subscriber"]

    return bottle.template("views/kspov.tpl", igra=igra, id_igre=id_igre, is_subscriber=is_subscriber)

@bottle.route('/zgodovina_kspov', method=['GET','HEAD'])
def prikazi_zgodovino():
    if request.method == 'HEAD':
        response.status = 200
        return

    uporabnik = request.get_cookie("uporabnik", secret=STARI_SLOVENSKI_PREGOVOR)
    mail = request.get_cookie("mail", secret=STARI_SLOVENSKI_PREGOVOR)
    if not uporabnik:
        response.status = 303
        response.set_header("Location", "/")
        return

    # server→server call to Data MS
    seznam_iger = model.data_kspov_history(mail)
    return bottle.template("views/zgodovina_kspov.tpl", igre=seznam_iger, uporabnik=uporabnik.upper())

@bottle.route('/brisi_kspov', method=['DELETE','HEAD'])
@log_request
@rate_limit(max_requests=20, window_seconds=60)
def brisi_igre_kps():
    if request.method == 'HEAD':
        response.status = 200
        return

    uporabnik = request.get_cookie("mail", secret=STARI_SLOVENSKI_PREGOVOR)
    if not uporabnik:
        response.status = 401
        return
    
    model.data_delete_kspov(uporabnik)
    response.status = 303
    response.set_header("Location", "/zgodovina_kspov")
    return

app = bottle.default_app()

if __name__ == "__main__":
    bottle.run(app=app, host="localhost", port=8080, debug=True)