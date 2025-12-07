import os
import json
import bottle
import threading
import model
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

# Za testiranje ----------------------
#@bottle.route('/', method=['GET','HEAD'])
#def root():
#    if request.method == 'HEAD':
#        response.status = 200
#        return
#    response.status = 303
#    response.set_header("Location", "/igra/")
#    return
## Za testiranje ----------------------
#
#@bottle.route('/igra/', method=['GET','HEAD'])
#def igra():
#    if request.method == 'HEAD':
#        response.status = 200
#        return
#    else:
#        uporabnik = bottle.request.get_cookie("uporabnik", secret=STARI_SLOVENSKI_PREGOVOR)
#        # Za testiranje ----------------------
#        if uporabnik is None:
#            uporabnik = "Gost"
#        # Za testiranje ----------------------
#        
#        # ZA POTREBE TESTIRANJA ZAKOMENTIRANO
#        # if uporabnik is None:
#        #     response.status = 303
#        #     response.set_header("Location", "/")
#        #     return
#        # else:
#        return bottle.template('views/igra.tpl', uporabnik=uporabnik.upper())

#================================================================================================================================================

def compute_ksp_state(id_igre: int, is_subscriber: bool):
    if id_igre not in ksp.igre:
        return {"action": "new_game"}

    igra = ksp.igre[id_igre]
    finished = igra.zmaga_igralca() or igra.zmaga_racunalnika()

    if finished:
        if is_subscriber:
            threading.Thread(
                # target=ksp.insert_game_ksp,
                args=(id_igre, igra.koncni_izid_igralca(), igra.koncni_izid_racunalnika()),
                daemon=True,
            ).start()
        else:
            ksp.igre.pop(id_igre, None)
            ksp.shrani_v_datoteko()
            ksp.nastavi_id(len(ksp.igre))

    return {
        "action": "ok",
        "id_igre": id_igre,
        "is_subscriber": is_subscriber,
        "finished": finished,
        "igra": {
            "delni_izid_igralca": igra.delni_izid_igralca(),
            "delni_izid_racunalnika": igra.delni_izid_racunalnika(),
            "koncni_izid_igralca": igra.koncni_izid_igralca(),
            "koncni_izid_racunalnika": igra.koncni_izid_racunalnika(),
            "zmaga_igralca": igra.zmaga_igralca(),
            "zmaga_racunalnika": igra.zmaga_racunalnika(),
        },
    }

@bottle.post("/ksp/nova")
def ksp_new():
    """Ustvari novo igro in vrni njen ID kot JSON."""
    id_nova_igra = ksp.nova_igra()

    response.content_type = "application/json"
    return json.dumps({"id_igre": id_nova_igra})

@bottle.route("/ksp/state", method=["GET"])
def api_ksp_state():
    try:
        id_igre = int(request.query.get("id_igre"))
    except (TypeError, ValueError):
        response.status = 400
        return {"error": "id_igre parameter is required and must be int"}

    is_subscriber = request.query.get("is_subscriber") == "1"

    result = compute_ksp_state(id_igre, is_subscriber)

    response.content_type = "application/json"
    return json.dumps(result)

@bottle.post("/ksp/poteza")
def ksp_move_api():
    data = request.json or {}
    try:
        id_igre = int(data.get("id_igre"))
        orozje = int(data.get("orozje"))
    except (TypeError, ValueError):
        response.status = 400
        return {"error": "id_igre and orozje must be integers"}

    is_subscriber = bool(data.get("is_subscriber"))

    # 1) izvede potezo na modelu
    ksp.potek_igre(id_igre, orozje)

    # 2) vrne morda samo OK (frontend bo itak še enkrat klical /ksp/state)
    response.content_type = "application/json"
    return json.dumps({"status": "ok"})
#====================================================================================================================================================

def compute_kspov_state(id_igre: int, is_subscriber: bool):
    if id_igre not in kspov.igre:
        return {"action": "new_game"}

    igra = kspov.igre[id_igre]
    finished = igra.zmaga_igralca_1() or igra.zmaga_racunalnika_1()

    if finished:
        if is_subscriber:
            threading.Thread(
                # target=kspov.insert_game_kspov,
                args=(id_igre, igra.koncni_izid_igralca_1(), igra.koncni_izid_racunalnika_1()),
                daemon=True,
            ).start()
        else:
            kspov.igre.pop(id_igre, None)
            kspov.shrani_v_datoteko()
            kspov.nastavi_id(len(kspov.igre))

    return {
        "action": "ok",
        "id_igre": id_igre,
        "is_subscriber": is_subscriber,
        "finished": finished,
        "igra": {
            "delni_izid_igralca": igra.delni_izid_igralca(),
            "delni_izid_racunalnika": igra.delni_izid_racunalnika(),
            "koncni_izid_igralca": igra.koncni_izid_igralca_1(),
            "koncni_izid_racunalnika": igra.koncni_izid_racunalnika_1(),
            "zmaga_igralca": igra.zmaga_igralca_1(),
            "zmaga_racunalnika": igra.zmaga_racunalnika_1(),
        },
    }

@bottle.post("/kspov/nova")
def kspov_new():
    """Ustvari novo igro in vrni njen ID kot JSON."""
    id_nova_igra = kspov.nova_igra_1()

    response.content_type = "application/json"
    return json.dumps({"id_igre": id_nova_igra})

@bottle.route("/kspov/state", method=["GET"])
def api_kspov_state():
    try:
        id_igre = int(request.query.get("id_igre"))
    except (TypeError, ValueError):
        response.status = 400
        return {"error": "id_igre parameter is required and must be int"}

    is_subscriber = request.query.get("is_subscriber") == "1"

    result = compute_kspov_state(id_igre, is_subscriber)

    response.content_type = "application/json"
    return json.dumps(result)

@bottle.post("/kspov/poteza")
def kspov_move_api():
    data = request.json or {}
    try:
        id_igre = int(data.get("id_igre"))
        orozje = int(data.get("orozje"))
    except (TypeError, ValueError):
        response.status = 400
        return {"error": "id_igre and orozje must be integers"}

    is_subscriber = bool(data.get("is_subscriber"))

    # 1) izvede potezo na modelu
    kspov.potek_igre(id_igre, orozje)

    # 2) vrne morda samo OK (frontend bo itak še enkrat klical /kspov/state)
    response.content_type = "application/json"
    return json.dumps({"status": "ok"})

app = bottle.default_app()

if __name__ == "__main__":
    bottle.run(app=app, host="127.0.0.1", port=8001, debug=True, reloader=True)