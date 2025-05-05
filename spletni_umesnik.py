import os
import json
import model
import bottle
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from hypercorn.middleware import AsyncioWSGIMiddleware

load_dotenv()

ID_IGRE_COKOLADNI_PISKOT = "id_igre"
STARI_SLOVENSKI_PREGOVOR = os.environ["SESSION_COOKIE_SECRET"]

ksp = model.KSP()
kspov = model.KSPOV()

@bottle.error(404)
def error404(error):
    return bottle.template('views/error.tpl')
    
@bottle.error(500)
def error500(error):
    return bottle.template('views/error.tpl')

@bottle.route('/static/<filepath:path>')
def server_static(filepath):
    return bottle.static_file(filepath, root='static')

@bottle.get('/')
def zacetni_menu():
    return bottle.template('views/log.tpl')

@bottle.get('/end/')
def zacetni_menu():
    uporabnik = bottle.request.get_cookie("uporabnik", secret=STARI_SLOVENSKI_PREGOVOR)
    if uporabnik is None:
        return bottle.redirect(f"/")
    else:
        return bottle.template('views/zacetni_menu.tpl', uporabnik=uporabnik.upper())

@bottle.put("/zacetni_menu/")
def prijava():
    uporabnik = bottle.request.json.get("uporabnik")
    if uporabnik == "Gost" or uporabnik == "":
        uporabnik = "Gost"
    
    ksp.nastavi_uporabnika(uporabnik)
    kspov.nastavi_uporabnika(uporabnik)

    ksp.preberi_iz_datoteke()
    kspov.preberi_iz_datoteke()

    bottle.response.set_cookie("uporabnik", uporabnik, path='/',secret=STARI_SLOVENSKI_PREGOVOR)
    return bottle.redirect(f"/end/")

#================================================================================================================================================

@bottle.get('/nova_igra_ksp/')
def nova_igra():
    id_nova_igra = ksp.nova_igra()
    # print(id_nova_igra)
    bottle.response.set_cookie(ID_IGRE_COKOLADNI_PISKOT, str(id_nova_igra), path='/', secret=STARI_SLOVENSKI_PREGOVOR)
    return bottle.redirect(f'/ksp/')

@bottle.get('/ksp/')
def igra_ksp():
    id_igre = bottle.request.get_cookie(ID_IGRE_COKOLADNI_PISKOT, secret=STARI_SLOVENSKI_PREGOVOR)
    if id_igre is None:
        return bottle.redirect(f"/nova_igra_ksp/")
    else:
        id_igre = int(id_igre)
        if id_igre not in ksp.igre:
            return bottle.redirect(f"/nova_igra_ksp/")
        
        # print(id_igre)
        igra = ksp.igre[id_igre]
        return bottle.template("views/ksp.tpl", igra=igra, id_igre=id_igre)

@bottle.post('/ksp/')
def izbira_igralca_ksp():
    id_igre = int(bottle.request.get_cookie(ID_IGRE_COKOLADNI_PISKOT, secret=STARI_SLOVENSKI_PREGOVOR))
    orozje = int(bottle.request.forms["orozje"])
    ksp.potek_igre(id_igre, orozje)
    return bottle.redirect(f"/ksp/")

@bottle.get("/zgodovina_ksp/")
def prikazi_zgodovino():
    uporabnik = bottle.request.get_cookie("uporabnik", secret=STARI_SLOVENSKI_PREGOVOR)
    if uporabnik is None:
        return bottle.redirect(f"/")
    
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

@bottle.delete('/brisi_ksp/')
def brisi_igre_kps():
    ksp.igre.clear()
    ksp.shrani_v_datoteko()
    return bottle.redirect(f"/zgodovina_ksp/")

@bottle.get("/zgodovina_ksp/json/")
def zgodovina_json():
    ksp.preberi_iz_datoteke()
    igre = [
        {"id": id_igre, "igralec": igra.igralec, "racunalnik": igra.racunalnik}
        for id_igre, igra in ksp.igre.items()
    ]
    bottle.response.content_type = 'application/json'
    return json.dumps(igre, indent=4)

@bottle.get("/zgodovina_ksp/xml/")
def zgodovina_xml():
    ksp.preberi_iz_datoteke()
    root = ET.Element("igre")
    for id_igre, igra in ksp.igre.items():
        igra_el = ET.SubElement(root, "igra", id=str(id_igre))
        ET.SubElement(igra_el, "igralec").text = str(igra.igralec)
        ET.SubElement(igra_el, "racunalnik").text = str(igra.racunalnik)

    bottle.response.content_type = 'application/xml'
    return ET.tostring(root, encoding="unicode")
#====================================================================================================================================================

@bottle.get("/nova_igra_kspov/")
def nova_igra_1():
    id_nova_igra = kspov.nova_igra_1()
    # print(id_nova_igra)
    bottle.response.set_cookie(ID_IGRE_COKOLADNI_PISKOT, str(id_nova_igra), path='/', secret=STARI_SLOVENSKI_PREGOVOR)
    return bottle.redirect(f'/kspov/')

@bottle.get('/kspov/')
def igra_ksp():
    id_igre = bottle.request.get_cookie(ID_IGRE_COKOLADNI_PISKOT, secret=STARI_SLOVENSKI_PREGOVOR)
    if id_igre is None:
        return bottle.redirect(f"/nova_igra_kspov/")
    else:
        id_igre = int(id_igre)
        if id_igre not in kspov.igre:
            return bottle.redirect(f"/nova_igra_kspov/")
        
        # print(id_igre)
        igra = kspov.igre[id_igre]
        return bottle.template("views/kspov.tpl", igra=igra, id_igre=id_igre)

@bottle.post('/kspov/')
def izbira_igralca_kspov():
    id_igre = int(bottle.request.get_cookie(ID_IGRE_COKOLADNI_PISKOT, secret=STARI_SLOVENSKI_PREGOVOR))
    orozje = int(bottle.request.forms["orozje"])
    kspov.potek_igre_1(id_igre, orozje)
    return bottle.redirect(f"/kspov/")

@bottle.get("/zgodovina_kspov/")
def prikazi_zgodovino():
    uporabnik = bottle.request.get_cookie("uporabnik", secret=STARI_SLOVENSKI_PREGOVOR)
    if uporabnik is None:
        return bottle.redirect(f"/")
    
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

@bottle.delete('/brisi_kspov/')
def brisi_igre_kps():
    kspov.igre.clear()
    kspov.shrani_v_datoteko()
    return bottle.redirect(f"/zgodovina_kspov/")

@bottle.get("/zgodovina_kspov/json/")
def zgodovina_json():
    kspov.preberi_iz_datoteke()
    igre = [
        {"id": id_igre, "igralec": igra.igralec, "racunalnik": igra.racunalnik}
        for id_igre, igra in kspov.igre.items()
    ]
    bottle.response.content_type = 'application/json'
    return json.dumps(igre, indent=4)

@bottle.get("/zgodovina_kspov/xml/")
def zgodovina_xml():
    kspov.preberi_iz_datoteke()
    root = ET.Element("igre")
    for id_igre, igra in kspov.igre.items():
        igra_el = ET.SubElement(root, "igra", id=str(id_igre))
        ET.SubElement(igra_el, "igralec").text = str(igra.igralec)
        ET.SubElement(igra_el, "racunalnik").text = str(igra.racunalnik)

    bottle.response.content_type = 'application/xml'
    return ET.tostring(root, encoding="unicode")

app = bottle.default_app()
asgi_app = AsyncioWSGIMiddleware(app)