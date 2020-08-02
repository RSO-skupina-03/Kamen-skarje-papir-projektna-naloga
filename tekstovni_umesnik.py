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
            print('DOBRODOŠLI V IGRI KAMEN ŠKARJE PAPIR')
            kamen_skarje_papir()
        elif izbira == '2':
            kamen_skarje_papir_ogenj_voda()
        elif izbira == '3':
            print('Nasvidenje')
            break
        else:
            print('Vpišite številko 1, 2 ali 3')

def kamen_skarje_papir():


    print('''
    Izberite si orožje:
    1: Kamen
    2: Škarje
    3: Papir
        ''')

    izbira = input('> ')
    prava_izbira = izbira.lower()

    if prava_izbira == 'kamen' or prava_izbira =='1':
        KamenSkarjePapir(0)
    elif prava_izbira == 'škarje' or prava_izbira == '2':
        KamenSkarjePapir(1)
    elif prava_izbira == 'papir' or prava_izbira == '3':
        KamenSkarjePapir(2)
    else:
        print('Vpišite ime orožja ali pa številko pred orožjem')



def kamen_skarje_papir_ogenj_voda():
    print('''
    DOBRODOŠLI V IGRI KAMEN ŠKARJE PAPIR OGENJ
    
    Izberite si orožje:
    1: Kamen
    2: Škarje
    3: Papir
    4: Ogenj
    5: Voda
    ''')

    izbira = input('> ')
    prava_izbira = izbira.lower()

    if prava_izbira == 'kamen' or prava_izbira =='1':
        KamenSkarjePapirOgenjVoda(0)
    elif prava_izbira == 'škarje' or prava_izbira == '2':
        KamenSkarjePapirOgenjVoda(1)
    elif prava_izbira == 'kamen' or prava_izbira == '3':
        KamenSkarjePapirOgenjVoda(2)
    elif prava_izbira == 'ogenj' or prava_izbira == '4':
        KamenSkarjePapirOgenjVoda(3)
    elif prava_izbira == 'voda' or prava_izbira == '5':
        KamenSkarjePapirOgenjVoda(4) 
    else:
        print('Vpišite ime orožja ali pa številko pred orožjem')
zacetni_menu()






