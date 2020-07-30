from random import randint

MOZNOSTI = ['Kamen', 'Skarje', 'Papir']

class KamenSkarjePapir:

    def __init__(self):
        self.moznost = [None, None]
        # Na [0] mestu je možnost, ki jo je izbral igralec, na [1] je možnoat ki jo je izbral računalnik
        self.racunalnik = 0
        self.igralec = 0
        # Spremeba!!! igra do 7 iger in se bo potem določilo zmagovalca
    def tocka_za_igralca(self):
        return self.igralec += 1

    def tocka_za_racunalnik(self):
        return self.racunalnik += 1

    def konec_igre(self):
        return self.igralec + self.racunalnik == 7
    
    def zmaga_igralca(self):
        return self.igralec > self.racunalnik

    def poraz_igralca(self):
        return self.igralec < self.racunalnik

        
    def potek_igre(self):
        while self.konec_igre() == False:
            if self.racunalnik == self.igralec:
                pass
            elif self.racunalnik == 'Kamen':
                if self.igralec == 'Papir':
                    return self.tocka_za_igralca()
                else:
                    return self.tocka_za_racunalnik()
            elif self.racunalnik == 'Skarje':
                if self.igralec == 'Kamen':
                    return self.tocka_za_igralca
                else:
                    return self.tocka_za_racunalnik()
            elif self.racunalnik == 'Papir':
                if self.igralec == 'Skarje':
                    return self.tocka_za_igralca()
                else:
                    return self.izguba_zivljenja_igralec()
            else:
                return self.poraz()

def nova_igra():
    return KamenSkarjePapir()


        