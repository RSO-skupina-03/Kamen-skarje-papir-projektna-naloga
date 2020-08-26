import model

# začetek tekstovnega umesnika da nekako vidim kako bom oblikoval program
def poraz_ali_zmaga(igra):
    if igra.zmaga_igralca() == True:
        return f'BRAVO, ZMAGAL SI MOGOČNI STROJ Z IZIDOM: {igralec(igra.koncni_izid_igralca())} : {racunalnik(igra.koncni_izid_racunalnika())}'
    else:
        return  f'IZGUBIL SI PROTI RAČUNALNIKU Z IZIDOM: {racunalnik(igra.koncni_izid_racunalnika())} : {igralec(igra.koncni_izid_igralca())}'
def poraz_ali_zmaga_1(igra):
    if igra.zmaga_igralca_1() == True:
        return f'BRAVO, ZMAGAL SI MOGOČNI STROJ Z IZIDOM: {igralec(igra.koncni_izid_igralca_1())} : {racunalnik(igra.koncni_izid_racunalnika_1())}'
    else:
        return f'IZGUBIL SI PROTI RAČUNALNIKU Z IZIDOM: {racunalnik(igra.koncni_izid_racunalnika_1())} : {igralec(igra.koncni_izid_igralca_1())}'

def delni_rezultat(igra):
    return f'TRENUTNI IZID: {igralec(igra.delni_izid_igralca())} : {racunalnik(igra.delni_izid_racunalnika())}'

def izbrano_orozje_racunalnik(igra):
    racunalnik = igra.izberi_orozje_racunalnik()
    return print('RAČUNALNIK:', racunalnik)

def izbrano_orozje_racunalnik_1(igra):
    racunalnik = igra.izberi_orozje_1_racunalnik()
    return print('RACUNALNIK:', racunalnik)

def krepko(niz):
    return f'\033[1m{niz}\033[0m'

def igralec(niz):
    return f'\033[1;94m{niz}\033[0m'

def racunalnik(niz):
    return f'\033[1;91m{niz}\033[0m'


def orozje_igralca():
    try:
        izbira = input('> ')
        prava_izbira = int(izbira) - 1
        return prava_izbira
    except ValueError:
            print('Prosim vnesite številko pred orožjem')

#============================================================================================================================================

def zacetni_menu():
    while True:

        print('''IZBERI SI IGRO:
        1: Kamen škarje papir (igraš proti računalniku minimalno 7 iger)
        2: Kamnen škraje papir ogenj voda (bolj atraktivna različica kjer se igra minimalno 14 iger)
        3: Zaključil sem z igranjem''')

        izbira = input('VPIŠITE IZBIRO: ')

        if izbira == '1':
            ksp = model.nova_igra()
            print(krepko('DOBRODOŠLI V IGRI KAMEN ŠKARJE PAPIR'))
            kamen_skarje_papir(ksp)
        elif izbira == '2':
            kspov = model.nova_igra_1()
            print(krepko('DOBRODOŠLI V IGRI KAMEN ŠKARJE PAPIR OGENJ'))
            kamen_skarje_papir_ogenj_voda(kspov)
        elif izbira == '3':
            print(krepko('Nasvidenje'))
            break
        else:
            print('Vpišite številko 1, 2 ali 3')

#==================================================================================================================================================

def kamen_skarje_papir(ksp):

    print('''
    Izberite si orožje:
    1: Kamen
    2: Škarje
    3: Papir
        ''')

    while ksp.konec_igre() == False:
        print(delni_rezultat(ksp))

        prava_izbira = orozje_igralca()
        izbrano_orozje_racunalnik(ksp)
    
        if prava_izbira == 0 or prava_izbira == 1 or prava_izbira == 2:
            ksp.potek_igre(prava_izbira)
        else:
            print('Vpišite številko pred orožjem')
    print(poraz_ali_zmaga(ksp))

#========================================================================================================================================================

def kamen_skarje_papir_ogenj_voda(kspov):
    print('''
    
    Izberite si orožje:
    1: Kamen
    2: Škarje
    3: Papir
    4: Ogenj
    5: Voda''')

    while kspov.konec_igre_1() == False:
        print(delni_rezultat(kspov))

        prava_izbira = orozje_igralca()
        izbrano_orozje_racunalnik_1(kspov)

        if prava_izbira == 0 or prava_izbira == 1 or prava_izbira == 2 or prava_izbira == 3 or prava_izbira == 4:
            kspov.potek_igre_1(prava_izbira)
        else:
            print('Vpišite ime orožja ali pa številko pred orožjem')
    print(poraz_ali_zmaga_1(kspov))

#==========================================================================================================================================================

zacetni_menu()






