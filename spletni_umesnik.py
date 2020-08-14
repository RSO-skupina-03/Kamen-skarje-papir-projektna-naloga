import model
import bottle

ksp = model.nova_igra()


@bottle.get('/')
def zacetni_menu():
    return bottle.template('views/zacetni_menu.tpl')

@bottle.get('/ksp/')
def igra_ksp():
    igra = model.nova_igra()
    return bottle.template('views/kps.tpl', igra=igra)

@bottle.get('/kspov/')
def igra_kspov():
    igra = model.nova_igra_1()
    return bottle.template('views/kspov.tpl', igra=igra)


@bottle.post('/kps/')
def izbira_igralca_ksp():
    orozje = int(bottle.request.forms['orozje'])

    while kps.konec_igre() == False:
        ksp.potek_igre(orozje)

    bottle.redirect('/ksp/')

@bottle.post('/ksp_nova/')
def ksp_nova():
     bottle.redirect('/kps/')

#@bottle.post('/kspov/')
#def izbira_igralca_kspov():
    #orozje = int(bottle.request.forms['orozje'])

    #while kspov.konec_igre_1() == False:
        #kspov.potek_igre_1(orozje)

    #bottle.redirect('/kspov/')
bottle.run(debug=True, reloader=True)





