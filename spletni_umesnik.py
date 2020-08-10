import model
import bottle



@bottle.get('/')
def zacetni_menu():
    return bottle.template('views/zacetni_menu.tpl')

@bottle.get('/ksp/')
def igra_ksp():
    kps = model.nova_igra()

    while kps.konec_igre() == False:
        prava_izbira = orozje

    if prava_izbira == 0 or prava_izbira == 1 or prava_izbira == 2:
        ksp.potek_igre(prava_izbira)
    else:
        pass

@bottle.get('/kspov/')
def igra_kspov():
    pass


@bottle.post('/kps/')
def izbira_igralca_ksp():
    orozje = int(bottle.request.forms['orozje'])
    model.KamenSkarjePapir().potek_igre(orozje)
    bottle.redirect('/ksp/')

@bottle.post('/kspov/')
def izbira_igralca_kspov():
    orozje = int(bottle.request.forms['orozje'])
    model.KamenSkarjePapirOgenjVoda().potek_igre_1(orozje)
    bottle.redirect('/kspov/')





