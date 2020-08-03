import model

# začetek tekstovnega umesnika da nekako vidim kako bom oblikoval program
def poraz_ali_poraz(igra):
    if igra.zmaga_igralca() == True:
        return f'BRAVO, ZMAGAL SI MOGOČNI STROJ Z IZIDOM: {igra.koncni_izid_igralca()} : {igra.koncni_izid_racunalnika()}'
    else:
        return  f'IZGUBIL SI PROTI RAČUNALNIKU Z IZIDOM: {igra.koncni_izid_racunalnika()} : {igra.koncni_izid_igralca()}'
def poraz_ali_poraz_1(igra):
    if igra.zmaga_igralca_1 == True:
        return f'BRAVO, ZMAGAL SI MOGOČNI STROJ Z IZIDOM: {igra.koncni_izid_igralca()} : {igra.koncni_izid_racunalnika()}'
    else:
        return f'IZGUBIL SI PROTI RAČUNALNIKU Z IZIDOM: {igra.koncni_izid_racunalnika()} : {igra.koncni_izid_igralca()}'

def delni_rezultat(igra):
    return f'TRENUTNI IZID: {igra.delni_izid_igralca()} : {igra.delni_izid_racunalnika()}'

def zacetni_menu():
    while True:

        print('''IZBERI SI IGRO:
        1: Kamen škarje papir (igraš proti računalniku minimalno 7 iger)
        2: Kamnen škraje papir ogenj voda (bolj atraktivna različica kjer se igra minimalno 14 iger)
        3: Zaključil sem z igranjem''')

        izbira = input('VPIŠITE IZBIRO: ')

        if izbira == '1':
            ksp = model.nova_igra()
            print('DOBRODOŠLI V IGRI KAMEN ŠKARJE PAPIR')
            kamen_skarje_papir(ksp)
        elif izbira == '2':
            kspov = model.nova_igra_1()
            print('DOBRODOŠLI V IGRI KAMEN ŠKARJE PAPIR OGENJ')
            kamen_skarje_papir_ogenj_voda(kspov)
        elif izbira == '3':
            print('Nasvidenje')
            break
        else:
            print('Vpišite številko 1, 2 ali 3')

def kamen_skarje_papir(ksp):

    print('''
    Izberite si orožje:
    1: Kamen
    2: Škarje
    3: Papir
        ''')

    while ksp.konec_igre() == False:
        print(delni_rezultat(ksp))

        izbira = input('> ')
        racunalnik = ksp.izberi_orozje_racunalnik()
        
        print('RAČUNALNIK:', racunalnik)
        prava_izbira = int(izbira) - 1

        if prava_izbira == 0 or prava_izbira == 1 or prava_izbira == 2:
            ksp.potek_igre(prava_izbira)
        else:
            print('Vpišite številko pred orožjem')
    print(poraz_ali_poraz(ksp))

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

        izbira = input('> ')
        racunalnik = kspov.izberi_orozje_racunalnik()

        print('RAČUNALNIK:', racunalnik)
        prava_izbira = int(izbira) - 1

        if prava_izbira == 0 or prava_izbira == 1 or prava_izbira == 2 or prava_izbira == 3 or prava_izbira == 4:
            kspov.potek_igre_1(prava_izbira)
        else:
            print('Vpišite ime orožja ali pa številko pred orožjem')
    print(poraz_ali_poraz(kspov))

zacetni_menu()






