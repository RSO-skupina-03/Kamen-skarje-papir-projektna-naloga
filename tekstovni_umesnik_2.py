import kamen_skarje_papir

# začetek tekstovnega umesnika da nekako vidim kako bom oblikoval program
def poraz_1(kamen_skarje_papir):
    return  f'IZGUBIL SI PROTI RAČUNALNIKU Z IZIDOM: \n 
     {self.koncni_izid_racunalnika_1()} : {self.koncni_izid_igralca_1()}'

def zmaga_1(kamen_skarje_papir):
    return f'BRAVO, ZMAGAL SI MOGOČNI STROJ Z IZIDOM: \n 
     {self.koncni_izid_igralca_1()} : {self.koncni_izid_racunalnika_1()}'

def delni_rezultat(kamen_skarje_papir):
    return f'TRENUTNI IZID: \n
    {self.delni_izid_igralca()} : {self.delni_izid_racunalnika()} '

def izbira():
    return input('IZBERI SI OROŽJE:')

def pozeni_umesnik():
    nova_igra = kamen_skarje_papir.nova_igra_1()
    while True:
        print(delni_rezultat(nova_igra))

        orozje = izbira()
        tretutni_rezultat = nova_igra.delni_rezultat()

        if nova_igra.zmaga_igralca():
            print(zmaga_1(nova_igra))
            break
        if nova_igra.poraz_igralca():
            print(poraz_1(nova_igra))
            break

pozeni_umesnik()