import model
import bottle

ID_IGRE_COKOLADNI_PISKOT = "id_igre"
STARI_SLOVENSKI_PREGOVOR = "Kdor drugemu luknjo koplje, sam vanjo pade"

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
    return bottle.template('views/zacetni_menu.tpl')

@bottle.put("/zacetni_menu/")
def prijava():
    uporabnik = bottle.request.json.get("uporabnik")

    if uporabnik == "Gost" or uporabnik == "":
        ksp.nastavi_uporabnika("Gost")
        kspov.nastavi_uporabnika("Gost")
    else:
        ksp.nastavi_uporabnika(uporabnik)
        kspov.nastavi_uporabnika(uporabnik)

    ksp.preberi_iz_datoteke()
    kspov.preberi_iz_datoteke()
    # tukaj shraniš uporabnika v sejo/cookie itd., če hočeš
    # zaenkrat lahko samo redirect na igro ali pozdrav
    return  bottle.redirect(f"/end/")

#================================================================================================================================================

@bottle.post("/nova_igra_ksp/")
def nova_igra():
    id_nova_igra = ksp.nova_igra()
    print(id_nova_igra)
    bottle.response.set_cookie(ID_IGRE_COKOLADNI_PISKOT, str(id_nova_igra), path='/', secret=STARI_SLOVENSKI_PREGOVOR)
    bottle.redirect(f'/ksp/')

@bottle.get('/ksp/')
def igra_ksp():
    id_igre = int(bottle.request.get_cookie(ID_IGRE_COKOLADNI_PISKOT, secret=STARI_SLOVENSKI_PREGOVOR))
    igra = ksp.igre[id_igre]
    return bottle.template("views/ksp.tpl", igra=igra, id_igre=id_igre)

@bottle.post('/ksp/')
def izbira_igralca_ksp():
    id_igre = int(bottle.request.get_cookie(ID_IGRE_COKOLADNI_PISKOT, secret=STARI_SLOVENSKI_PREGOVOR))
    orozje = int(bottle.request.forms["orozje"])
    ksp.potek_igre(id_igre, orozje)
    bottle.redirect(f"/ksp/")

@bottle.get("/zgodovina_ksp/")
def prikazi_zgodovino():
    ksp.preberi_iz_datoteke()
    igre = ksp.igre

    seznam_iger = []
    for id_igre, igra in igre.items():
        opis = f"ID {id_igre}: igralec - {igra.igralec}, računalnik - {igra.racunalnik}"
        seznam_iger.append(opis)
        
    return bottle.template("views/zgodovina.tpl", igre=seznam_iger)

#====================================================================================================================================================

@bottle.post("/nova_igra_kspov/")
def nova_igra_1():
    id_nova_igra = kspov.nova_igra_1()
    print(id_nova_igra)
    bottle.response.set_cookie(ID_IGRE_COKOLADNI_PISKOT, str(id_nova_igra), path='/', secret=STARI_SLOVENSKI_PREGOVOR)
    bottle.redirect(f'/kspov/')

@bottle.get('/kspov/')
def igra_kspov():
    id_igre = int(bottle.request.get_cookie(ID_IGRE_COKOLADNI_PISKOT, secret=STARI_SLOVENSKI_PREGOVOR))
    igra = kspov.igre[id_igre]
    return bottle.template("views/kspov.tpl", igra=igra, id_igre=id_igre)

@bottle.post('/kspov/')
def izbira_igralca_kspov():
    id_igre = int(bottle.request.get_cookie(ID_IGRE_COKOLADNI_PISKOT, secret=STARI_SLOVENSKI_PREGOVOR))
    orozje = int(bottle.request.forms["orozje"])
    kspov.potek_igre_1(id_igre, orozje)
    bottle.redirect(f"/kspov/")

@bottle.get("/zgodovina_kspov/")
def prikazi_zgodovino():
    kspov.preberi_iz_datoteke()
    igre = kspov.igre

    seznam_iger = []
    for id_igre, igra in igre.items():
        opis = f"ID {id_igre}: igralec - {igra.igralec}, računalnik - {igra.racunalnik}"
        seznam_iger.append(opis)
        
    return bottle.template("views/zgodovina.tpl", igre=seznam_iger)

app = bottle.default_app()





