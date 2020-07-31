from random import randint

MOZNOSTI = ['Kamen', 'Skarje', 'Papir']
MOZNOSTI_2 = ['Kamen', 'Skarje', 'Papir', 'Voda', 'Ogenj']

class Igra:

    def __init__(self):
        self.orozje = [None, None]
        # Na [0] mestu je možnost, ki jo je izbral igralec, na [1] je možnoat ki jo je izbral računalnik
        self.racunalnik = 0
        self.igralec = 0

    def tocka_za_igralca(self):
        return self.igralec += 1

    def tocka_za_racunalnik(self):
        return self.racunalnik += 1
    
    def delni_izid_igralca(self):
        return self.igralec
    
    def delni_izid_racunalnika(self):
        return self.racunalnik

class KamenSkarjePapir(Igra):
    # Sprememba!!! igra do 7 iger in se bo potem določilo zmagovalca

    def konec_igre(self):
        return self.igralec + self.racunalnik == 7
    
    def zmaga_igralca(self):
        return self.igralec > self.racunalnik and self.konec_igre() == True

    def poraz_igralca(self):
        return self.igralec < self.racunalnik and self.konec_igre() == True

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
class KamenSkarjePapirOgenjVoda(Igra):

    def zmaga_igralca_1(self):
        return self.igralec > self.racunalnik and self.konec_igre_1() == True

    def poraz_igralca_1(self):
        return self.igralec < self.racunalnik and self.konec_igre_1() == True

    def konec_igre_1(self):
        return self.racunalnik + self.igralec == 15
        #tukaj se bo igra igrala do 15 iger
    def koncni_izid_racunalnika_1(self):
        if self.konec_igre_1() == True:
            return self.racunalnik
        else:
            pass

    def koncni_izid_igralca_1(self):
        if self.konec_igre_1() == True:
            return self.igralec
        else:
            pass
    
    def izberi_orozje_1 (self):

        racunalnik = MOZNOSTI_2[randint(0, 4)]
        igralec = MOZNOSTI_2[1] # to bo igralec sam določil kaj bo igral
        pass

    def potek_igre_1(self):

        igralec = self.orozje[0].upper()[0]
        racunalnik = self.orozje[1].upper()[0]

        while self.konec_igre_1 == False:
            if igralec == racunalnik:
                continue
            elif racunalnik == 'K':
                if igralec == 'P' or igralec == 'O':
                    return self.tocka_za_igralca()
                else:
                    return self.tocka_za_racunalnik()
            elif racunalnik == 'S':
                if igralec == 'K' or igralec == 'O':
                    return self.tocka_za_igralca()
                else:
                    return self.tocka_za_racunalnik()
            elif racunalnik == 'P':
                if igralec == 'S' or igralec == 'O':
                    return self.tocka_za_igralca()
                else:
                    return self.tocka_za_racunalnik()
            elif racunalnik == 'O':
                if igralec == 'V':
                    return self.tocka_za_igralca()
                else:
                    return self.tocka_za_racunalnik()
            elif racunalnik == 'V':
                if igralec == 'S' or igralec == 'K' or igralec == 'P':
                    return self.tocka_za_igralca()
                else:
                    return self.tocka_za_racunalnik()
            else:
                pass


#def nova_igra():
    #return KamenSkarjePapir()


        