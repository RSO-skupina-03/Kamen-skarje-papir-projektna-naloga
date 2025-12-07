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

# Za testiranje ----------------------
@bottle.route('/', method=['GET','HEAD'])
def root():
    if request.method == 'HEAD':
        response.status = 200
        return
    response.status = 303
    response.set_header("Location", "/igra/")
    return
# Za testiranje ----------------------

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

        # Za testiranje ----------------------
        raw = bottle.request.get_cookie("narocnik", secret=STARI_SLOVENSKI_PREGOVOR)
        if raw:
            is_subscriber = "subscribers" in json.loads(raw)
        else:
            is_subscriber = False
        # Za testiranje ----------------------
        
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

        # Za testiranje ----------------------
        raw = bottle.request.get_cookie("narocnik", secret=STARI_SLOVENSKI_PREGOVOR)
        if raw:
            is_subscriber = "subscribers" in json.loads(raw)
        else:
            is_subscriber = False
        # Za testiranje ----------------------
        
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

app = bottle.default_app()

if __name__ == "__main__":
    bottle.run(app=app, host="0.0.0.0", port=8000, debug=True, reloader=True)