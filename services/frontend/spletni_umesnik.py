import os
import json
import model
import bottle
import threading
import requests
from bottle import request, response
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

load_dotenv()

ID_IGRE_COKOLADNI_PISKOT = "id_igre"
STARI_SLOVENSKI_PREGOVOR = os.environ["SESSION_COOKIE_SECRET"]
DB_URL = os.environ["DB_URL"]

ksp = model.KSP()
kspov = model.KSPOV()

# @bottle.error(404)
# def error404(error):
#     return bottle.template('views/error.tpl')
# 
# @bottle.error(401)
# def error401(error):
#     return bottle.template('views/error.tpl')
# 
# @bottle.error(500)
# def error500(error):
#     return bottle.template('views/error.tpl')

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
    return json.dumps({"status": "healthy", "service": "ksp-app"})

@bottle.route('/ready', method=['GET', 'HEAD'])
def readiness_check():
    """Readiness probe - checks if the application is ready to serve traffic"""
    if request.method == 'HEAD':
        response.status = 200
        return
    
    # Check required environment variables
    checks = {
        "status": "ready",
        "service": "ksp-app",
        "checks": {}
    }
    
    # Check if required environment variables are set
    try:
        session_secret = os.environ.get("SESSION_COOKIE_SECRET")
        db_url = os.environ.get("DB_URL")
        
        checks["checks"]["environment"] = {
            "SESSION_COOKIE_SECRET": "ok" if session_secret else "missing",
            "DB_URL": "ok" if db_url else "missing"
        }
        
        # Check if data directory is writable
        try:
            datoteke_dir = 'datoteke'
            if not os.path.exists(datoteke_dir):
                os.makedirs(datoteke_dir, exist_ok=True)
            # Try to write a test file
            test_file = os.path.join(datoteke_dir, '.health_check')
            with open(test_file, 'w') as f:
                f.write('ok')
            os.remove(test_file)
            checks["checks"]["filesystem"] = "ok"
        except Exception as e:
            checks["checks"]["filesystem"] = f"error: {str(e)}"
        
        # Determine overall readiness
        all_ok = (
            session_secret and 
            db_url and 
            checks["checks"]["filesystem"] == "ok"
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

# testiranje game engine
@bottle.route('/', method=['GET','HEAD'])
def login():
     if request.method == 'HEAD':
         response.status = 200
         return
     else:
         valid = request.query.get("valid","1") != "0"
         response.status = 303
         response.set_header("Location", "/igra/")
         return

@bottle.route('/igra/', method=['GET','HEAD'])
def igra():
    if request.method == 'HEAD':
        response.status = 200
        return
    else:
        uporabnik = bottle.request.get_cookie("uporabnik", secret=STARI_SLOVENSKI_PREGOVOR)
        # Za testiranje ----------------------
        if uporabnik is None:
            uporabnik = "Gost"
        # Za testiranje ----------------------
        
        # ZA POTREBE TESTIRANJA ZAKOMENTIRANO
        # if uporabnik is None:
        #     response.status = 303
        #     response.set_header("Location", "/")
        #     return
        # else:
        return bottle.template('views/igra.tpl', uporabnik=uporabnik.upper())
        
@bottle.route('/login/', method=['OPTIONS'])
def login_preflight():
    response.set_header('Access-Control-Allow-Origin',  '*')
    response.set_header('Access-Control-Allow-Methods', 'PUT, OPTIONS')
    response.set_header('Access-Control-Allow-Headers', 'Content-Type')
    return

@bottle.route("/login/", method=["PUT","HEAD"])
def login():
    if request.method == "HEAD":
        response.status = 303
        response.set_header("Location", "/igra/")
        return
    else:
        user = bottle.request.json.get("uporabnik")
        password = bottle.request.json.get("password")
        sub = ""
        uporabnik = ""
        if user == "Gost" or user == "":
            uporabnik = "Gost"
            sub = json.dumps(['non-subscribers'])
        # Tukaj dodaj logiko za OAuth2 avtentikacijo
        #else:
        #
        #    
        #    info = ldap_authenticate_and_get_info(user, password)
        #    
        #    if info is None:
        #        response.status = 303
        #        response.set_header("Location", "/?valid=0")
        #        return
        #    
        #    print(info["cn"] + " " + info["sn"] + " " + json.dumps(info["groups"]))
        #    uporabnik = info["cn"] + " " + info["sn"]
        #    sub = json.dumps(info["groups"])

    
        bottle.response.set_cookie("uporabnik", uporabnik, path='/',secret=STARI_SLOVENSKI_PREGOVOR)
        bottle.response.set_cookie("narocnik", sub, path='/',secret=STARI_SLOVENSKI_PREGOVOR)

        ksp.nastavi_uporabnika(user)
        kspov.nastavi_uporabnika(user)

        is_subscriber = "subscribers" in json.loads(sub)
        # print(json.loads(sub))
        if is_subscriber:
            kspov.get_id_kspov()
            ksp.get_id_ksp()
            threading.Thread(ksp.load_user_history_ksp(),daemon=True).start()
            threading.Thread(kspov.load_user_history_kspov(),daemon=True).start()
        else:
            ksp.nastavi_id(len(ksp.igre))
            kspov.nastavi_id(len(kspov.igre))

        print(ksp.id, kspov.id)
        print("\n")

        ksp.preberi_iz_datoteke()
        kspov.preberi_iz_datoteke()

        response.status = 303
        response.set_header("Location", "/igra/")
        return

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
            f"http://127.0.0.1:8001/ksp/poteza",
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
        r = requests.post(f"http://127.0.0.1:8001/ksp/nova", timeout=10.0)
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
            f"http://127.0.0.1:8001/ksp/state",
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
#====================================================================================================================================================    
bottle.post("/kspov/")
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
        response.set_header("Location", "/")
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
            f"http://127.0.0.1:8001/kspov/poteza",
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
    response.set_header("Location", "/")
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
        r = requests.post(f"http://127.0.0.1:8001/kspov/nova", timeout=10.0)
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
    response.set_header("Location", "/")
    return

# Za testiranje
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
            f"http://127.0.0.1:8001/kspov/state",
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
    bottle.run(app=app, host="127.0.0.1", port=8000, debug=True, reloader=True)