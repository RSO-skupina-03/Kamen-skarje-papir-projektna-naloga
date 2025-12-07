import os
import json
import model
import bottle
import threading
from bottle import request, response
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

load_dotenv()

ID_IGRE_COKOLADNI_PISKOT = "id_igre"
STARI_SLOVENSKI_PREGOVOR = os.environ["SESSION_COOKIE_SECRET"]
DB_URL = os.environ["DB_URL"]

ksp = model.KSP()
kspov = model.KSPOV()

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

@bottle.route('/', method=['GET','HEAD'])
def login():
    if request.method == 'HEAD':
        response.status = 200
        return
    else:
        valid = request.query.get("valid","1") != "0"
        return bottle.template('views/log.tpl', valid=valid)

@bottle.route('/igra/', method=['GET','HEAD'])
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

@bottle.route('/nova_igra_ksp/', method=['GET','HEAD'])
def nova_igra():
    if request.method == 'HEAD':
        response.status = 303
        response.set_header("Location", "/ksp/")
        return
    else:
        id_nova_igra = ksp.nova_igra()
        print(id_nova_igra)
        bottle.response.set_cookie(ID_IGRE_COKOLADNI_PISKOT, str(id_nova_igra), path='/', secret=STARI_SLOVENSKI_PREGOVOR)
        response.status = 303
        response.set_header("Location", "/ksp/")
        return
    
@bottle.route('/ksp/', method=['GET','HEAD'])
def igra_ksp():
    if request.method == 'HEAD':
        response.status = 200
        return
    else:
        id_igre = bottle.request.get_cookie(ID_IGRE_COKOLADNI_PISKOT, secret=STARI_SLOVENSKI_PREGOVOR)
        raw = bottle.request.get_cookie("narocnik", secret=STARI_SLOVENSKI_PREGOVOR)
        is_subscriber = "subscribers" in json.loads(raw)
        if id_igre is None:
            response.status = 303
            response.set_header("Location", "/nova_igra_ksp/")
            return
        else:
            id_igre = int(id_igre)
            if id_igre not in ksp.igre:
                response.status = 303
                response.set_header("Location", "/nova_igra_ksp/")
                return
        
            # print(id_igre)
            igra = ksp.igre[id_igre]
            if igra.zmaga_igralca() or igra.zmaga_racunalnika():
                if is_subscriber:
                    threading.Thread(target=ksp.insert_game_ksp(id_igre, igra.koncni_izid_igralca(), igra.koncni_izid_racunalnika()), daemon=True).start()
                else:
                    ksp.igre.pop(id_igre, None)
                    ksp.shrani_v_datoteko()
                    ksp.nastavi_id(len(ksp.igre))
            return bottle.template("views/ksp.tpl", igra=igra, id_igre=id_igre, is_subscriber=is_subscriber)


@bottle.route('/ksp/', method=['POST','HEAD'])
def izbira_igralca_ksp():
    if request.method == 'HEAD':
        response.status = 303
        response.set_header("Location", "/ksp/")
        return
    else:
        id_igre = int(bottle.request.get_cookie(ID_IGRE_COKOLADNI_PISKOT, secret=STARI_SLOVENSKI_PREGOVOR))
        orozje = int(bottle.request.forms["orozje"])
        ksp.potek_igre(id_igre, orozje)
        response.status = 303
        response.set_header("Location", "/ksp/")
        return

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
    
        ksp.preberi_iz_datoteke()
        igre_za_brisanje = [id_igre for id_igre, igra in ksp.igre.items() if igra.igralec == 0 and igra.racunalnik == 0]
        for id_igre in igre_za_brisanje:
            del ksp.igre[id_igre]
        ksp.shrani_v_datoteko()

        seznam_iger = []
        for id_igre, igra in ksp.igre.items():
            if igra.igralec > 0 or igra.racunalnik > 0:
                opis = f"ID {id_igre}: igralec - {igra.igralec}, računalnik - {igra.racunalnik}"
                seznam_iger.append(opis)
        return bottle.template("views/zgodovina_ksp.tpl", igre=seznam_iger, uporabnik=uporabnik.upper())

@bottle.route('/brisi_ksp/', method=['DELETE','HEAD'])
def brisi_igre_kps():
    if request.method == 'HEAD':
        response.status = 303
        response.set_header("Location", "/zgodovina_ksp/")
        return
    else:
        ksp.igre.clear()
        ksp.shrani_v_datoteko()
        raw = bottle.request.get_cookie("narocnik", secret=STARI_SLOVENSKI_PREGOVOR)
        is_subscriber = "subscribers" in json.loads(raw)
        if is_subscriber:
            threading.Thread(target=ksp.delete_ksp(), daemon=True).start()
        response.status = 303
        response.set_header("Location", "/zgodovina_ksp/")
        return

@bottle.route('/zgodovina_ksp/json/', method=['GET','HEAD'])
def zgodovina_json():
    if request.method == 'HEAD':
        response.status = 200
        return
    else:
        ksp.preberi_iz_datoteke()
        igre = [
            {"id": id_igre, "igralec": igra.igralec, "racunalnik": igra.racunalnik}
            for id_igre, igra in ksp.igre.items()
        ]
        bottle.response.content_type = 'application/json'
        return json.dumps(igre, indent=4)
    
@bottle.route('/zgodovina_ksp/xml/', method=['GET','HEAD'])
def zgodovina_xml():
    if request.method == 'HEAD':
        response.status = 200
        return
    else:
        ksp.preberi_iz_datoteke()
        root = ET.Element("igre")
        for id_igre, igra in ksp.igre.items():
            igra_el = ET.SubElement(root, "igra", id=str(id_igre))
            ET.SubElement(igra_el, "igralec").text = str(igra.igralec)
            ET.SubElement(igra_el, "racunalnik").text = str(igra.racunalnik)

        bottle.response.content_type = 'application/xml'
        return ET.tostring(root, encoding="unicode")
#====================================================================================================================================================

@bottle.route('/nova_igra_kspov/', method=['GET','HEAD'])
def nova_igra_1():
    if request.method == 'HEAD':
        response.status = 303
        response.set_header("Location", "/kspov/")
        return
    else:
        id_nova_igra = kspov.nova_igra_1()
        print(id_nova_igra)
        bottle.response.set_cookie(ID_IGRE_COKOLADNI_PISKOT, str(id_nova_igra), path='/', secret=STARI_SLOVENSKI_PREGOVOR)
        response.status = 303
        response.set_header("Location", "/kspov/")
        return
    
@bottle.route('/kspov/', method=['GET','HEAD'])
def igra_kspov():
    if request.method == 'HEAD':
        response.status = 303
        response.set_header("Location", "/kspov/")
        return
    else:
        id_igre = bottle.request.get_cookie(ID_IGRE_COKOLADNI_PISKOT, secret=STARI_SLOVENSKI_PREGOVOR)
        raw = bottle.request.get_cookie("narocnik", secret=STARI_SLOVENSKI_PREGOVOR)
        is_subscriber = "subscribers" in json.loads(raw)
        if id_igre is None:
            response.status = 303
            response.set_header("Location", "/nova_igra_kspov/")
            return
        else:
            id_igre = int(id_igre)
            if id_igre not in kspov.igre:
                response.status = 303
                response.set_header("Location", "/nova_igra_kspov/")
                return
        
            # print(id_igre)
            igra = kspov.igre[id_igre]
            if igra.zmaga_igralca_1() or igra.zmaga_racunalnika_1():
                if is_subscriber:
                    threading.Thread(target=kspov.insert_game_kspov(id_igre, igra.koncni_izid_igralca_1(), igra.koncni_izid_racunalnika_1()), daemon=True).start()
                else:
                    kspov.igre.pop(id_igre, None)
                    kspov.shrani_v_datoteko()
                    kspov.nastavi_id(len(kspov.igre))
            return bottle.template("views/kspov.tpl", igra=igra, id_igre=id_igre, is_subscriber=is_subscriber)
        
@bottle.route('/kspov/', method=['POST','HEAD'])
def izbira_igralca_kspov():
    if request.method == 'HEAD':
        response.status = 303
        response.set_header("Location", "/kspov/")
        return
    else:
        id_igre = int(bottle.request.get_cookie(ID_IGRE_COKOLADNI_PISKOT, secret=STARI_SLOVENSKI_PREGOVOR))
        orozje = int(bottle.request.forms["orozje"])
        kspov.potek_igre_1(id_igre, orozje)
        response.status = 303
        response.set_header("Location", "/kspov/")
        return

@bottle.route('/zgodovina_kspov/', method=['GET','HEAD'])
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
    
        kspov.preberi_iz_datoteke()
        igre_za_brisanje = [id_igre for id_igre, igra in kspov.igre.items() if igra.igralec == 0 and igra.racunalnik == 0]
        for id_igre in igre_za_brisanje:
            del kspov.igre[id_igre]
        kspov.shrani_v_datoteko()

        seznam_iger = []
        for id_igre, igra in kspov.igre.items():
            if igra.igralec > 0 or igra.racunalnik > 0:
                opis = f"ID {id_igre}: igralec - {igra.igralec}, računalnik - {igra.racunalnik}"
                seznam_iger.append(opis)
        return bottle.template("views/zgodovina_kspov.tpl", igre=seznam_iger, uporabnik=uporabnik.upper())

@bottle.route('/brisi_kspov/', method=['DELETE','HEAD'])
def brisi_igre_kpsov():
    if request.method == 'HEAD':
        response.status = 303
        response.set_header("Location", "/zgodovina_kspov/")
        return
    else:
        kspov.igre.clear()
        kspov.shrani_v_datoteko()
        raw = bottle.request.get_cookie("narocnik", secret=STARI_SLOVENSKI_PREGOVOR)
        is_subscriber = "subscribers" in json.loads(raw)
        if is_subscriber:
            threading.Thread(target=ksp.delete_kspov(), daemon=True).start()
        response.status = 303
        response.set_header("Location", "/zgodovina_kspov/")
        return

@bottle.route('/zgodovina_kspov/json/', method=['GET','HEAD'])
def zgodovina_json():
    if request.method == 'HEAD':
        response.status = 200
        return
    else:
        kspov.preberi_iz_datoteke()
        igre = [
            {"id": id_igre, "igralec": igra.igralec, "racunalnik": igra.racunalnik}
            for id_igre, igra in kspov.igre.items()
        ]
        bottle.response.content_type = 'application/json'
        return json.dumps(igre, indent=4)
    
@bottle.route('/zgodovina_kspov/xml/', method=['GET','HEAD'])
def zgodovina_xml():
    if request.method == 'HEAD':
        response.status = 200
        return
    else:
        kspov.preberi_iz_datoteke()
        root = ET.Element("igre")
        for id_igre, igra in kspov.igre.items():
            igra_el = ET.SubElement(root, "igra", id=str(id_igre))
            ET.SubElement(igra_el, "igralec").text = str(igra.igralec)
            ET.SubElement(igra_el, "racunalnik").text = str(igra.racunalnik)

        bottle.response.content_type = 'application/xml'
        return ET.tostring(root, encoding="unicode")

app = bottle.default_app()

# if __name__ == "__main__":
    #bottle.run(app=app, host="0.0.0.0", port=8000, debug=True, reloader=True)

# @app.hook('after_request')
# def advertise_http3():
    # xresponse.set_header('Alt-Svc', 'h3=":4433"; h3-29=":4433"; ma=86400')

# @app.hook('before_request')
# def enforce_https():
    # Če pride neprenjujen klic po http://
    # if request.urlparts.scheme != 'https':
        # secure = request.urlparts._replace(scheme='https').geturl()
        # return redirect(secure, code=301)
# Ves promet se preumseri na https 303 ali 302 redirect

# @app.hook('after_request')
# def set_hsts():
    # response.set_header('Strict-Transport-Security', 'max-age=63072000; includeSubDomains; preload')
# Naj se vedno uporabljajo HTTPS zahtevki

# response.set_cookie("uporabnik", uporabnik, secret=STARI_SLOVENSKI_PREGOVOR, path="/", secure=True, httponly=True)
# da ga brskalik lahko pošilja le po HTTPS povezavi

# asgi_app = AsyncioWSGIMiddleware(app)