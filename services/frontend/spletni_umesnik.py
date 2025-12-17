import os
import json
import bottle
import requests
from bottle import request, response
from dotenv import load_dotenv

load_dotenv()

ID_IGRE_COKOLADNI_PISKOT = "id_igre"
STARI_SLOVENSKI_PREGOVOR = os.environ["SESSION_COOKIE_SECRET"]
GAME_ENGINE_URL = os.environ["GAME_ENGINE_URL"]
AUTH_LOCAL=os.environ["AUTH_LOCAL"]

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
        
        checks["checks"]["environment"] = {
            "SESSION_COOKIE_SECRET": "ok" if session_secret else "missing",
            "GAME_ENGINE_URL": "ok" if game_engine_url else "missing",
            "FRONTEND_URL": "ok" if frontend_url else "missing",
            "AUTH_URL": "ok" if auth_url else "missing"
        }

        # Determine overall readiness
        all_ok = (
            session_secret and 
            game_engine_url and
            frontend_url and
            auth_url
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
def env_js():
    cfg = {
        "AUTH_URL": os.environ["AUTH_URL"],
        "FRONTEND_URL": os.environ["FRONTEND_URL"],
    }
    response.content_type = "application/javascript; charset=utf-8"
    return "window.__ENV__ = " + json.dumps(cfg) + ";"

@bottle.route('/', method=['GET','HEAD'])
def login():
    if request.method == 'HEAD':
        response.status = 200
        return
    else:
        valid = request.query.get("valid","1") != "0"
        return bottle.template('views/log.tpl', valid=valid)
            
@bottle.route('/login/', method=['OPTIONS'])
def login_preflight():
    response.set_header('Access-Control-Allow-Origin',  '*')
    response.set_header('Access-Control-Allow-Methods', 'PUT, OPTIONS')
    response.set_header('Access-Control-Allow-Headers', 'Content-Type')
    return

@bottle.route("/login/", method=["PUT", "HEAD"])
def login():
    if request.method == "HEAD":
        response.status = 303
        response.set_header("Location", "/igra")
        return

    data = request.json or {}
    user = data.get("uporabnik", "")
    password = data.get("password", "")

    # za zdaj: Gost ali prazen = guest, ostalo obravnavaj kot subscriber
    sub = ""
    if user == "Gost" or user == "":
        uporabnik = "Gost"
        sub = json.dumps(["non-subscribers"])
    else:
        # tu bi šla prava OAuth/LDAP logika – zaenkrat na hard:
        uporabnik = user
        sub = json.dumps(["subscribers"])

    response.set_cookie("uporabnik", user, path="/", secret=STARI_SLOVENSKI_PREGOVOR)
    response.set_cookie("narocnik", sub, path="/", secret=STARI_SLOVENSKI_PREGOVOR)

    # 2) povej game_engine-u, kdo je user in ali je subscriber
    try:
        r = requests.post(
            f"{GAME_ENGINE_URL}/ksp/init_user",
            json={
                "uporabnik": uporabnik,
                "mail": uporabnik,
                "is_subscriber": sub,
            },
            timeout=5.0,
        )
    except requests.RequestException as e:
        response.status = 502
        return f"Game engine unavailable: {e}"

    if r.status_code != 200:
        response.status = 502
        return f"Game engine error: {r.status_code} {r.text}"

    # (opcijsko: data = r.json() in logiraš, uporabljaš ksp_id, kspov_id, ...)

    # 3) redirect na /igra (ali /ksp/, kakor imaš urejen UI)
    response.status = 303
    response.set_header("Location", "/igra")
    return

@bottle.get("/auth/finalize")
def finalize():
    ticket = bottle.request.query.get("ticket")
    if not ticket:
        bottle.abort(400, "Missing ticket")

    # back-channel call to auth (server-to-server)
    r = requests.post(f"{AUTH_LOCAL}/auth/redeem",
                      json={"ticket": ticket}, timeout=(3,10))
    r.raise_for_status()
    data = r.json()

    uporabnik = data.get("name","")
    mail = data.get("email","")
    sub = data.get("sub", "")

    # set cookies on the FRONTEND origin
    bottle.response.set_cookie("uporabnik", data.get("name",""), path="/", secret=STARI_SLOVENSKI_PREGOVOR)
    bottle.response.set_cookie("narocnik", sub, path="/", secret=STARI_SLOVENSKI_PREGOVOR)

    try:
        r = requests.post(
            f"{GAME_ENGINE_URL}/ksp/init_user",
            json={
                "uporabnik": uporabnik,
                "mail": mail,
                "is_subscriber": True,
            },
            timeout=5.0,
        )
    except requests.RequestException as e:
        response.status = 502
        return f"Game engine unavailable: {e}"

    if r.status_code != 200:
        response.status = 502
        return f"Game engine error: {r.status_code} {r.text}"

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
@bottle.post("/ksp/")
def izbira_igralca_ksp_frontend():
    # 1) id igre iz cookie-ja
    id_cookie = request.get_cookie(
        ID_IGRE_COKOLADNI_PISKOT,
        secret=STARI_SLOVENSKI_PREGOVOR,
    )
    if id_cookie is None:
        response.status = 303
        response.set_header("Location", "/nova_igra_ksp/")
        return

    # 2) izbrano orožje iz formularja
    try:
        orozje = int(request.forms.get("orozje"))
    except (TypeError, ValueError):
        # nič ni izbral → samo reload
        response.status = 303
        response.set_header("Location", "/ksp/")
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
    try:
        r = requests.post(
            f"{GAME_ENGINE_URL}/ksp/poteza",
            json={
                "id_igre": int(id_cookie),
                "orozje": orozje,
                "is_subscriber": is_subscriber,
            },
            timeout=5.0,
        )
    except requests.RequestException as e:
        response.status = 502
        return f"Game engine unavailable: {e}"

    if r.status_code != 200:
        response.status = 502
        return f"Game engine error: {r.status_code} {r.text}"

    # 5) po potezi gremo nazaj na GET (da se nova situacija nariše)
    response.status = 303
    response.set_header("Location", "/ksp/")
    return

@bottle.route("/nova_igra_ksp/", method=["GET", "HEAD"])
def nova_igra_ksp_frontend():
    if request.method == "HEAD":
        # HEAD vprašanje še vedno rečemo "bo nova igra"
        response.status = 303
        response.set_header("Location", "/")
        return

    # 1) klic na game_engine, da ustvari novo igro
    try:
        r = requests.post(f"{GAME_ENGINE_URL}/ksp/nova", timeout=10.0)
    except requests.RequestException as e:
        response.status = 502
        return f"Game engine unavailable: {e}"

    if r.status_code != 200:
        response.status = 502
        return f"Game engine error: {r.status_code} {r.text}"

    data = r.json()
    id_nova_igra = data["id_igre"]

    # 2) nastavimo cookie z ID-jem igre
    response.set_cookie(ID_IGRE_COKOLADNI_PISKOT, str(id_nova_igra), path="/", secret=STARI_SLOVENSKI_PREGOVOR,)

    # 3) preusmerimo nazaj na "/" (kjer bo klic /ksp/state)
    response.status = 303
    response.set_header("Location", "/ksp/")
    return

@bottle.route("/ksp/", method=["GET", "HEAD"])
def igra_ksp_frontend():
    if request.method == "HEAD":
        response.status = 200
        return

    # 1) preberemo piškotke
    id_cookie = request.get_cookie(ID_IGRE_COKOLADNI_PISKOT, secret=STARI_SLOVENSKI_PREGOVOR)
    # Za testiranje ----------------------
    raw = bottle.request.get_cookie("narocnik", secret=STARI_SLOVENSKI_PREGOVOR)
    if raw:
        is_subscriber = "subscribers" in json.loads(raw)
    else:
        is_subscriber = False
     # Za testiranje ----------------------

    # če ni id_igre → frontend odloči, da rabimo novo igro
    if id_cookie is None:
        response.status = 303
        response.set_header("Location", "/nova_igra_ksp/")
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
    try:
        r = requests.get(
            f"{GAME_ENGINE_URL}/ksp/state",
            params={
                "id_igre": id_cookie,
                "is_subscriber": "1" if is_subscriber else "0",
            },
            timeout=10.0,
        )
    except requests.RequestException as e:
        response.status = 502
        return f"Game engine unavailable: {e}"

    if r.status_code != 200:
        response.status = 502
        return f"Game engine error: {r.status_code} {r.text}"

    data = r.json()

    # 3) frontend spet samo odloči, kaj narediti
    if data.get("action") == "new_game":
        response.status = 303
        response.set_header("Location", "/nova_igra_ksp/")
        return

    # action == "ok"
    igra = data["igra"]
    id_igre = data["id_igre"]
    is_subscriber = data["is_subscriber"]

    return bottle.template("views/ksp.tpl", igra=igra, id_igre=id_igre, is_subscriber=is_subscriber)

@bottle.route('/zgodovina_ksp/', method=['GET','HEAD'])
def prikazi_zgodovino():
    if request.method == 'HEAD':
        response.status = 200
        return
    else:
        uporabnik = bottle.request.get_cookie("uporabnik", secret=STARI_SLOVENSKI_PREGOVOR)
        if uporabnik is None:
            response.status = 303
            response.set_header("Location", "/")
            return
        
        # To implementiraj klic na backend, ki ni blokirajoc
        # ksp.preberi_iz_datoteke()
        # igre_za_brisanje = [id_igre for id_igre, igra in ksp.igre.items() if igra.igralec == 0 and igra.racunalnik == 0]
        # for id_igre in igre_za_brisanje:
        #     del ksp.igre[id_igre]
        # ksp.shrani_v_datoteko()
        return bottle.template("views/zgodovina_ksp.tpl", igre=seznam_iger, uporabnik=uporabnik.upper())
#====================================================================================================================================================    
@bottle.post("/kspov/")
def izbira_igralca_kspov_frontend():
    # 1) id igre iz cookie-ja
    id_cookie = request.get_cookie(
        ID_IGRE_COKOLADNI_PISKOT,
        secret=STARI_SLOVENSKI_PREGOVOR,
    )
    if id_cookie is None:
        response.status = 303
        response.set_header("Location", "/nova_igra_kspov/")
        return

    # 2) izbrano orožje iz formularja
    try:
        orozje = int(request.forms.get("orozje"))
    except (TypeError, ValueError):
        # nič ni izbral → samo reload
        response.status = 303
        response.set_header("Location", "/kspov/")
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
    try:
        r = requests.post(
            f"{GAME_ENGINE_URL}/kspov/poteza",
            json={
                "id_igre": int(id_cookie),
                "orozje": orozje,
                "is_subscriber": is_subscriber,
            },
            timeout=5.0,
        )
    except requests.RequestException as e:
        response.status = 502
        return f"Game engine unavailable: {e}"

    if r.status_code != 200:
        response.status = 502
        return f"Game engine error: {r.status_code} {r.text}"

    # 5) po potezi gremo nazaj na GET (da se nova situacija nariše)
    response.status = 303
    response.set_header("Location", "/kspov/")
    return

@bottle.route("/nova_igra_kspov/", method=["GET", "HEAD"])
def nova_igra_kspov_frontend():
    if request.method == "HEAD":
        # HEAD vprašanje še vedno rečemo "bo nova igra"
        response.status = 303
        response.set_header("Location", "/")
        return

    # 1) klic na game_engine, da ustvari novo igro
    try:
        r = requests.post(f"{GAME_ENGINE_URL}/kspov/nova", timeout=10.0)
    except requests.RequestException as e:
        response.status = 502
        return f"Game engine unavailable: {e}"

    if r.status_code != 200:
        response.status = 502
        return f"Game engine error: {r.status_code} {r.text}"

    data = r.json()
    id_nova_igra = data["id_igre"]

    # 2) nastavimo cookie z ID-jem igre
    response.set_cookie(ID_IGRE_COKOLADNI_PISKOT, str(id_nova_igra), path="/", secret=STARI_SLOVENSKI_PREGOVOR,)

    # 3) preusmerimo nazaj na "/" (kjer bo klic /kspov/state)
    response.status = 303
    response.set_header("Location", "/kspov/")
    return

@bottle.route("/kspov/", method=["GET", "HEAD"])
def igra_kspov_frontend():
    if request.method == "HEAD":
        response.status = 200
        return

    # 1) preberemo piškotke
    id_cookie = request.get_cookie(ID_IGRE_COKOLADNI_PISKOT, secret=STARI_SLOVENSKI_PREGOVOR)
    # Za testiranje ----------------------
    raw = bottle.request.get_cookie("narocnik", secret=STARI_SLOVENSKI_PREGOVOR)
    if raw:
        is_subscriber = "subscribers" in json.loads(raw)
    else:
        is_subscriber = False
     # Za testiranje ----------------------

    # če ni id_igre → frontend odloči, da rabimo novo igro
    if id_cookie is None:
        response.status = 303
        response.set_header("Location", "/nova_igra_kspov/")
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
    try:
        r = requests.get(
            f"{GAME_ENGINE_URL}/kspov/state",
            params={
                "id_igre": id_cookie,
                "is_subscriber": "1" if is_subscriber else "0",
            },
            timeout=10.0,
        )
    except requests.RequestException as e:
        response.status = 502
        return f"Game engine unavailable: {e}"

    if r.status_code != 200:
        response.status = 502
        return f"Game engine error: {r.status_code} {r.text}"

    data = r.json()

    # 3) frontend spet samo odloči, kaj narediti
    if data.get("action") == "new_game":
        response.status = 303
        response.set_header("Location", "/nova_igra_kspov/")
        return

    # action == "ok"
    igra = data["igra"]
    id_igre = data["id_igre"]
    is_subscriber = data["is_subscriber"]

    return bottle.template("views/kspov.tpl", igra=igra, id_igre=id_igre, is_subscriber=is_subscriber)

app = bottle.default_app()

if __name__ == "__main__":
    bottle.run(app=app, host="localhost", port=8080, debug=True)