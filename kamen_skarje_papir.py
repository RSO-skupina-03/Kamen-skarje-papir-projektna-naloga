from random import randint

MOZNOSTI = ['Kamen', 'Skarje', 'Papir']

class KamenSkarjePapir:

    def __init__(self):
        self.orozje = [None, None]
        # Na [0] mestu je možnost, ki jo je izbral igralec, na [1] je možnoat ki jo je izbral računalnik
        self.racunalnik = 0
        self.igralec = 0
        # Sprememba!!! igra do 7 iger in se bo potem določilo zmagovalca
    def tocka_za_igralca(self):
        return self.igralec += 1

    def tocka_za_racunalnik(self):
        return self.racunalnik += 1

    def konec_igre(self):
        return self.igralec + self.racunalnik == 7
    
    def zmaga_igralca(self):
        return self.igralec > self.racunalnik and self.konec_igre() == True

    def poraz_igralca(self):
        return self.igralec < self.racunalnik and self.konec_igre() == True
    
    def delni_izid_igralca(self):
        return self.igralec
    
    def delni_izid_racunalnika(self):
        return self.racunalnik
    
    def koncni_izid_racunalnika(self):
        if self.konec_igre() == True:
            return self.racunalnik
        else:
            pass

    def koncni_izid_igralca(self):
        if self.konec_igre() == True:
            return self.igralec
        else:
            pass
    def izberi_orozje(self):

        racunalnik = MOZNOSTI[randint(0, 2)]
        igralce = MOZNOSTI[1] # npr. potem bom dal na izbiro katero orožje lahko izbere

        pass

    def potek_igre(self):

        igralec = self.orozje[0].upper()[0]
        racunalnik = self.orozje[1].upper()[0]

        while self.konec_igre() == False:
            if igralec == racunalnik:
                continue
            elif racunalnik == 'K':
                if igralec == 'P':
                    return self.tocka_za_igralca()
                else:
                    return self.tocka_za_racunalnik()
            elif racunalnik == 'S':
                if igralec == 'K':
                    return self.tocka_za_igralca
                else:
                    return self.tocka_za_racunalnik()
            elif racunalnik == 'P':
                if igralec == 'S':
                    return self.tocka_za_igralca()
                else:
                    return self.tocka_za_racunalnik()
            else:
                pass

def nova_igra():
    return KamenSkarjePapir()


        