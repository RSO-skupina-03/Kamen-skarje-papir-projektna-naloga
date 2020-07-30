import kamen_skarje_papir

# začetek tekstovnega umesnika da nekako vidim kako bom oblikoval program
def poraz(kamen_skarje_papir):
    return  f'IZGUBIL SI PROTI RAČUNALNIKU Z IZIDOM:\n 
     {self.racunalnik} : {self.igralec}'


def zmaga(kamen_skarje_papir):
    return f'BRAVO, ZMAGAL SI MOGOČNI STROJ Z IZIDOM:\n 
     {self.igralec} : {self.racunalnik}'

def delni_rezultat(kamen_skarje_papir):
    return f'TRENUTNI IZID: \n
    {trenutni rezultat igralca} : {trenutni rezultat računalnika} '


def izbira():
    return input('IZBERI SI OROŽJE:')


def pozeni_umesnik():
    nova_igra = kamen_skarje_papir.nova_igra()
    while True:
        print(delni_rezultat(nova_igra))

        orozje = izbira()
        tretutni_rezultat = ???

        if nova_igra.zmaga_igralca():
            print(zmaga(nova_igra))
            break
        if nova_igra.poraz_igralca():
            print(poraz(nova_igra))
            break
        
pozeni_umesnik()