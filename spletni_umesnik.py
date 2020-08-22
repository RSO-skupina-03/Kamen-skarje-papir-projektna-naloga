import model
import bottle

ID_IGRE_COKOLADNI_PISKOT = "id_igre"
STARI_SLOVENSKI_PREGOVOR = "Kdor drugemu luknjo koplje, sam vanjo pade"

ksp = model.KSP()
kspov = model.KSPOV()


@bottle.get('/')
def zacetni_menu():
    return bottle.template('views/zacetni_menu.tpl')

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

bottle.run(debug=True, reloader=True)





