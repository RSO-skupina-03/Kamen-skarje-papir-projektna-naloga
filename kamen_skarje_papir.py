from random import randint

MOZNOSTI = ['Kamen', 'Skarje', 'Papir']

class KamenSkarjePapir:

    def __init__(self, igralec, racunalnik , kvadratek=5, srcek=5):
        self.racunalnik = MOZNOSTI[randint(0, 2)]
        self.igralec = 'Kamen'
        # tukaj moras narediti input za uporabnika da izbere
        self.kvadratek = 5
        self.srcek = 5
        # igra se bo igrala na 5 življenj, srcek je življenje uporabnika kvadratek je življenje računalnika
    def izguba_zivljenja_igralec(self):
        return self.kvadratek -= 1

    def izguba_zivljenja_racunalnik(self):
        return self.srcek -= 1
        
    def potek_igre(self):
        while self.srcek > 0 or self.kvadratek > 0:
            if self.racunalnik == self.igralec:
                pass
            elif self.racunalnik == 'Kamen':
                if self.igralec == 'Papir':
                    return self.izguba_zivljenja_racunalnik()
                else:
                    return self.izguba_zivljenja_igralec()
            elif self.racunalnik == 'Skarje':
                if self.igralec == 'Kamen':
                    return self.izguba_zivljenja_racunalnik()
                else:
                    return self.izguba_zivljenja_igralec()
            elif self.racunalnik == 'Papir':
                if self.igralec == 'Skarje':
                    return self.izguba_zivljenja_racunalnik()
                else:
                    return self.izguba_zivljenja_igralec()
            else:
                return self.poraz()

    def poraz(self):
        return self.srcek == 0
    
def nova_igra():
    return KamenSkarjePapir()


        