from random import randint

MOZNOSTI = ['Kamen', 'Skarje', 'Papir']
MOZNOSTI_2 = ['Kamen', 'Skarje', 'Papir', 'Voda', 'Ogenj']

class Igra:

    def __init__(self, orozje):
        self.orozje = orozje # v ta parameter se bo shtanjeval indeks, ki ga je igralec izbral za svoje orožje
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
    # Sprememba!!! igra se do 7 iger in se bo potem določilo zmagovalca

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

    def izberi_orozje_racunalnik(self):
        return MOZNOSTI[randint(0, 2)]

    def izberi_orozje_igralec(self):
        return MOZNOSTI[self.orozje] # npr. potem bom dal na izbiro katero orožje lahko izbere

    def potek_igre(self):

        slovar_izbir = {'Kamen': 0, 'Skarje': 1, 'Papir': 2}

        igralec = slovar_izbir.get(self.izberi_orozje_igralec())

        racunalnik = slovar_izbir.get(self.izberi_orozje_racunalnik())

        while self.konec_igre() == False:

            mozni_izidi = [
                [0, 1, -1],
                [-1, 0, 1],
                [1, -1, 0]
            ] # 1 pomeni, da je zmagal igralec -1 pomeni da je zmagal računalnik 0 pomeni izenačenje
            # igralec predstavlja vrstice, računalnik predstavlja stolpce
            rezultat = mozni_izidi[igralec][racunalnik]
            return rezultat

    def tocka(self):
        if self.potek_igre() == 1:
            return self.tocka_za_igralca()
        elif self.potek_igre() == -1:
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
    
    def izberi_orozje_1_racunalnik(self):
        return MOZNOSTI_2[randint(0, 4)]
    
    def izberi_orozje_1_igralec(self):
        return MOZNOSTI_2[self.orozje] # to bo igralec sam določil kaj bo igral

    def potek_igre_1(self):

        slovar_izbir = {'Kamen': 0, 'Skarje': 1, 'Papir': 2, 'Ogenj': 3, 'Voda': 4}

        igralec = slovar_izbir.get(self.izberi_orozje_1_igralec())

        racunalnik = slovar_izbir.get(self.izberi_orozje_1_racunalnik())

        while self.konec_igre_1() == False:

            mozni_izidi = [
                [0, 1, -1, -1, 1],
                [-1, 0, 1, -1, 1],
                [1, -1, 0, -1, 1],
                [1, 1, 1, 0, -1],
                [-1, -1, -1, 1, 0]
            ]

            rezultat = mozni_izidi[igralec][racunalnik]
            return rezultat

    def tocka_1(self):
        if self.potek_igre_1() == 1:
            return self.tocka_za_igralca()
        elif self.potek_igre_1() == -1:
            return self.tocka_za_racunalnik()
        else:
            pass



def nova_igra():
    orozje = 1 # tukaj bo multiple chooise
    return KamenSkarjePapir(orozje)

def nova_igra_1():
    orozje = 2
    return KamenSkarjePapirOgenjVoda(orozje)


        