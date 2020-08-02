from random import randint

MOZNOSTI = ['Kamen', 'Skarje', 'Papir']
MOZNOSTI_2 = ['Kamen', 'Skarje', 'Papir', 'Voda', 'Ogenj']

class Igra:

    def __init__(self, orozje):
        self.orozje = orozje # v ta parameter se bo shtanjeval indeks, ki ga je igralec izbral za svoje orožje
        self.igralec = 0
        self.racunalnik = 0

    def tocka_za_igralca(self):
        self.igralec += 1
    
    def tocka_za_racunalnik(self):
        self.racunalnik += 1
    
    def delni_izid_igralca(self):
        return self.igralec
    
    def delni_izid_racunalnika(self):
        return self.racunalnik

class KamenSkarjePapir(Igra):

    def __init__(self, orozje):
        super().__init__(orozje)
    # Sprememba!!! igra se do 7 iger in se bo potem določilo zmagovalca
        while self.konec_igre() == False:
            slovar_izbir = {'Kamen': 0, 'Skarje': 1, 'Papir': 2}

            igralec = slovar_izbir.get(self.izberi_orozje_igralec())
            racunalnik = slovar_izbir.get(self.izberi_orozje_racunalnik())

            mozni_izidi = [
                [0, 1, -1],
                [-1, 0, 1],
                [1, -1, 0]
            ] # 1 pomeni, da je zmagal igralec -1 pomeni da je zmagal računalnik 0 pomeni izenačenje
            # igralec predstavlja vrstice, računalnik predstavlja stolpce
            rezultat = mozni_izidi[igralec][racunalnik]

            if rezultat == 1:
                self.tocka_za_igralca()
            elif rezultat == -1:
                self.tocka_za_racunalnik()
            else:
                pass
    def izberi_orozje_racunalnik(self):
        return MOZNOSTI[randint(0, 2)]

    def izberi_orozje_igralec(self):
        return MOZNOSTI[self.orozje] # npr. potem bom dal na izbiro katero orožje lahko izbere

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

class KamenSkarjePapirOgenjVoda(Igra):

    def __init__(self, orozje):
        super().__init__(orozje)

        while self.konec_igre_1() == False:
            slovar_izbir = {'Kamen': 0, 'Skarje': 1, 'Papir': 2, 'Ogenj': 3, 'Voda': 4}

            igralec = slovar_izbir.get(self.izberi_orozje_1_igralec())
            racunalnik = slovar_izbir.get(self.izberi_orozje_1_racunalnik())


            mozni_izidi = [
                [0, 1, -1, -1, 1],
                [-1, 0, 1, -1, 1],
                [1, -1, 0, -1, 1],
                [1, 1, 1, 0, -1],
                [-1, -1, -1, 1, 0]
            ]

            rezultat = mozni_izidi[igralec][racunalnik]

            if rezultat == 1:
                self.tocka_za_igralca()
            elif rezultat == -1:
                self.tocka_za_racunalnik()
            else:
                pass
            
    def izberi_orozje_1_racunalnik(self):
        return MOZNOSTI_2[randint(0, 4)]
    
    def izberi_orozje_1_igralec(self):
        return MOZNOSTI_2[self.orozje] # to bo igralec sam določil kaj bo igral

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



        