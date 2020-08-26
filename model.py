from random import randint
import json

MOZNOSTI = ['Kamen', 'Škarje', 'Papir']
MOZNOSTI_2 = ['Kamen', 'Škarje', 'Papir', 'Voda', 'Ogenj']
DATOTEKA_KSP = 'datoteke/ksp.json'
DATOTEKA_KSPOV = 'datoteke/kspov.json'
ZACETEK = 'Zacetek'

class Igra:

    def __init__(self, igralec=0, racunalnik=0):
        self.igralec = igralec
        self.racunalnik = racunalnik

    def tocka_za_igralca(self):
        self.igralec += 1
    
    def tocka_za_racunalnik(self):
        self.racunalnik += 1
    
    def delni_izid_igralca(self):
        return self.igralec
    
    def delni_izid_racunalnika(self):
        return self.racunalnik

#============================================================================================================================================================

class KamenSkarjePapir(Igra):

    def potek_igre(self, izbrano_orozje):
    #igra se do 7 iger in se bo potem določilo zmagovalca
            slovar_izbir = {'Kamen': 0, 'Škarje': 1, 'Papir': 2}

            igralec = slovar_izbir.get(MOZNOSTI[izbrano_orozje])
            racunalnik = slovar_izbir.get(self.izberi_orozje_racunalnik())

            mozni_izidi = [
                [3, 1, 2],
                [2, 3, 1],
                [1, 2, 3]
            ] # 1 pomeni, da je zmagal igralec 2 pomeni da je zmagal računalnik 3 pomeni izenačenje
            # igralec predstavlja vrstice, računalnik predstavlja stolpce
            rezultat = mozni_izidi[igralec][racunalnik]

            if rezultat == 1:
                self.tocka_za_igralca()
            elif rezultat == 2:
                self.tocka_za_racunalnik()
            elif rezultat == 3:
                pass
            else:
                assert False

    def izberi_orozje_racunalnik(self):
        return MOZNOSTI[randint(0, 2)]

    def konec_igre(self):
        return self.igralec + self.racunalnik == 7
    
    def zmaga_igralca(self):
        return self.igralec > self.racunalnik and self.konec_igre() == True
    
    def zmaga_racunalnika(self):
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

#=========================================================================================================================================================

class KamenSkarjePapirOgenjVoda(Igra):

    def potek_igre_1(self, izbrano_orozje):

            slovar_izbir = {'Kamen': 0, 'Škarje': 1, 'Papir': 2, 'Ogenj': 3, 'Voda': 4}

            igralec = slovar_izbir.get(MOZNOSTI_2[izbrano_orozje])
            racunalnik = slovar_izbir.get(self.izberi_orozje_1_racunalnik())

            mozni_izidi = [
                [3, 1, 2, 2, 1],
                [2, 3, 1, 2, 1],
                [1, 2, 3, 2, 1],
                [1, 1, 1, 3, 2],
                [2, 2, 2, 1, 3]
            ]

            rezultat = mozni_izidi[igralec][racunalnik]

            if rezultat == 1:
                self.tocka_za_igralca()
            elif rezultat == 2:
                self.tocka_za_racunalnik()
            elif rezultat == 3:
                pass
            else:
                assert False
            
    def izberi_orozje_1_racunalnik(self):
        return MOZNOSTI_2[randint(0, 4)]
    
    def zmaga_igralca_1(self):
        return self.igralec > self.racunalnik and self.konec_igre_1() == True
    
    def zmaga_racunalnika_1(self):
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

#=========================================================================================================================================================
        
def nova_igra():
    return KamenSkarjePapir(igralec=0, racunalnik=0)

def nova_igra_1():
    return KamenSkarjePapirOgenjVoda(igralec=0, racunalnik=0)

#=========================================================================================================================================================

class Datoteka:

    def __init__(self):
        self.igre = {}
    
    def prosti_id_igre(self):
        if len(self.igre) == 0:
            return 0
        else:
            return len(self.igre) + 1

#============================================================================================================================================================
   
class KSP(Datoteka):

    def nova_igra(self):
        self.preberi_iz_datoteke()
        nov_id = self.prosti_id_igre()
        sveza_igra = nova_igra()
            
        self.igre[nov_id] = sveza_igra
        self.shrani_v_datoteko()
        return nov_id

    def potek_igre(self, id_igre, orozje):
        self.preberi_iz_datoteke()
        trenutna_igra = self.igre[id_igre]

        trenutna_igra.potek_igre(orozje)
        self.igre[id_igre] = trenutna_igra

        self.shrani_v_datoteko()

    def shrani_v_datoteko(self):
        igre = {}
        for id_igre, igra in self.igre.items():
            igre[id_igre] = (igra.igralec, igra.racunalnik)
        
        with open(DATOTEKA_KSP, 'w') as izhodna:
            json.dump(igre, izhodna, ensure_ascii=False, indent=2)

    def preberi_iz_datoteke(self):
        with open(DATOTEKA_KSP) as vhodna:
            igre = json.load(vhodna)

        self.igre = {}
        for id_igre, (igralec, racunalnik) in igre.items():
            self.igre[int(id_igre)] = KamenSkarjePapir(igralec, racunalnik)

#=========================================================================================================================================================

class KSPOV(Datoteka):

    def nova_igra_1(self):
        self.preberi_iz_datoteke()
        nov_id = self.prosti_id_igre()
        sveza_igra = nova_igra_1()

        self.igre[nov_id] = sveza_igra
        self.shrani_v_datoteko()
        return nov_id

    def potek_igre_1(self, id_igre, orozje):
        self.preberi_iz_datoteke()
        trenutna_igra = self.igre[id_igre]

        trenutna_igra.potek_igre_1(orozje)
        self.igre[id_igre] = trenutna_igra

        self.shrani_v_datoteko()

    def shrani_v_datoteko(self):
        igre = {}
        for id_igre, igra in self.igre.items():
            igre[id_igre] = (igra.igralec, igra.racunalnik)

        with open(DATOTEKA_KSPOV, 'w') as izhodna:
            json.dump(igre, izhodna, ensure_ascii=False, indent=2)

    def preberi_iz_datoteke(self):
        with open(DATOTEKA_KSPOV) as vhodna:
            igre = json.load(vhodna)

        self.igre = {}
        for id_igre, (igralec, racunalnik) in igre.items():
            self.igre[int(id_igre)] = KamenSkarjePapirOgenjVoda(igralec, racunalnik)

#pomembno je da beležim rezultat igre in sicer to lahko shranim v datoteko kot {id_igre: [igralec, racunalnik]



        