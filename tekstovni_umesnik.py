from model import KamenSkarjePapirOgenjVoda, KamenSkarjePapir

# začetek tekstovnega umesnika da nekako vidim kako bom oblikoval program
#def poraz(kamen_skarje_papir):
    #return  f'IZGUBIL SI PROTI RAČUNALNIKU Z IZIDOM: 
     #{self.koncni_izid_racunalnika()} : {self.koncni_izid_igralca()}'

#def zmaga(kamen_skarje_papir):
    #return f'BRAVO, ZMAGAL SI MOGOČNI STROJ Z IZIDOM:
     #{self.koncni_izid_igralca()} : {self.koncni_izid_racunalnika()}'

#def delni_rezultat(kamen_skarje_papir):
    #return f'TRENUTNI IZID:
    #{self.delni_izid_igralca()} : {self.delni_izid_racunalnika()} '

def zacetni_menu():
    while True:

        print('''IZBERI SI IGRO:
        1: Kamen škarje papir (igraš proti računalniku 7 iger)
        2: Kamnen škraje papir ogenj voda (bolj atraktivna različica kjer se igra 14 iger)
        3: Zaključil sem z igranjem''')

        izbira = input('VPIŠITE IZBIRO: ')

        if izbira == '1':
            ksp = KamenSkarjePapir()
            print('DOBRODOŠLI V IGRI KAMEN ŠKARJE PAPIR')
            kamen_skarje_papir(ksp)
        elif izbira == '2':
            kspov = KamenSkarjePapirOgenjVoda()
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

        izbira = input('> ')
        prava_izbira = int(izbira) - 1

        if prava_izbira == 0 or prava_izbira == 1 or prava_izbira == 2:
            ksp.potek_igre(prava_izbira)
        else:
            print('Vpišite številko pred orožjem')

def kamen_skarje_papir_ogenj_voda(kspov):
    print('''
    
    Izberite si orožje:
    1: Kamen
    2: Škarje
    3: Papir
    4: Ogenj
    5: Voda''')

    while kspov.konec_igre_1() == False:

        izbira = input('> ')
        prava_izbira = int(izbira) - 1

        if prava_izbira == 0 or prava_izbira == 1 or prava_izbira == 2 or prava_izbira == 3 or prava_izbira == 4:
            kspov.potek_igre_1(prava_izbira)
        else:
            print('Vpišite ime orožja ali pa številko pred orožjem')

zacetni_menu()






