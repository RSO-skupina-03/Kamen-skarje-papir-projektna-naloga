import os, json, requests
from random import randint
from dotenv import load_dotenv

load_dotenv()
MOZNOSTI = ['Kamen', 'Škarje', 'Papir']
MOZNOSTI_2 = ['Kamen', 'Škarje', 'Papir', 'Voda', 'Ogenj']
ZACETEK = 'Zacetek'

DATA_URL = os.environ["DATA_URL"]
DATOTEKA_KSP = os.environ["DATOTEKA_KSP"]
DATOTEKA_KSPOV = os.environ["DATOTEKA_KSPOV"]

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
        self.uporabnik = ""
        self.id = 0

    def nastavi_uporabnika(self, uporabnik):
        self.uporabnik = uporabnik

    def prosti_id_igre(self):
        self.id = self.id + 1
        return self.id
    
    def nastavi_id(self, id):
        self.id = id

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
        # Preberi obstoječe podatke
        if os.path.exists(DATOTEKA_KSP) and os.stat(DATOTEKA_KSP).st_size > 0:
            with open(DATOTEKA_KSP, "r", encoding="utf-8") as izhodna:
                vsi_uporabniki = json.load(izhodna)
        else:
            vsi_uporabniki = {}

        # Shranimo igre za trenutnega uporabnika
        vsi_uporabniki[self.uporabnik] = {
            id_igre: (igra.igralec, igra.racunalnik) for id_igre, igra in self.igre.items()
        }

        with open(DATOTEKA_KSP, "w", encoding="utf-8") as izhodna:
            json.dump(vsi_uporabniki, izhodna, ensure_ascii=False, indent=2)


    def preberi_iz_datoteke(self):
        if not os.path.exists(DATOTEKA_KSP) or os.stat(DATOTEKA_KSP).st_size == 0:
            self.igre = {}
            return

        with open(DATOTEKA_KSP, "r", encoding="utf-8") as vhodna:
            vsi_uporabniki = json.load(vhodna)

        # Preberi samo igre za prijavljenega uporabnika
        if self.uporabnik in vsi_uporabniki:
            igre = vsi_uporabniki[self.uporabnik]
            self.igre = {
                int(id_igre): KamenSkarjePapir(igralec, racunalnik)
                for id_igre, (igralec, racunalnik) in igre.items()
            }
        else:
            self.igre = {}


    def insert_game_ksp(self, game_id, player_score, computer_score) -> int:
        """
        Send an UPSERT request to the data/history microservice.
        Returns the number of affected rows reported by the service.
        """
        url = f"{DATA_URL}/data/ksp/insert"
        payload = {
            "username": self.uporabnik,
            "game_id": game_id,
            "player": player_score,
            "computer": computer_score,
        }

        try:
            r = requests.post(
                url,
                json=payload,
                timeout=(3, 10),  # 3s connect, 10s read
                headers={"Content-Type": "application/json"},
            )
            r.raise_for_status()
            data = r.json() if r.headers.get("content-type","").startswith("application/json") else {}
            return int(data.get("affected", 1))
        except requests.RequestException as e:
            raise RuntimeError(f"insert_game_ksp failed: {e}")

    def get_id_ksp(self):
        """
        Ask the Data microservice for a new game id and set it on this instance.
        Expects JSON like: {"id": 123} (also accepts "game_id" or "next_id").
        """
        url = f"{DATA_URL}/data/ksp/get/id"
        try:
            # If your service needs the username, send it along:
            r = requests.get(url, params={"username": self.uporabnik}, timeout=(2, 6))
            r.raise_for_status()
            payload = r.json() or {}

            # Accept common key names
            new_id = (payload.get("game_id"))
            if new_id is None:
                raise ValueError(f"Missing 'id' in response: {payload}")

            self.nastavi_id(int(new_id))
        except Exception as e:
            # Log + safe fallback
            print(f"[get_id_ksp] fetch from {url} failed: {e}", flush=True)
            self.nastavi_id(0)

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
        # Preberi obstoječe podatke
        if os.path.exists(DATOTEKA_KSPOV) and os.stat(DATOTEKA_KSPOV).st_size > 0:
            with open(DATOTEKA_KSPOV, "r", encoding="utf-8") as izhodna:
                vsi_uporabniki = json.load(izhodna)
        else:
            vsi_uporabniki = {}

        # Shranimo igre za trenutnega uporabnika
        vsi_uporabniki[self.uporabnik] = {
            id_igre: (igra.igralec, igra.racunalnik) for id_igre, igra in self.igre.items()
        }

        with open(DATOTEKA_KSPOV, "w", encoding="utf-8") as izhodna:
            json.dump(vsi_uporabniki, izhodna, ensure_ascii=False, indent=2)


    def preberi_iz_datoteke(self):
        if not os.path.exists(DATOTEKA_KSPOV) or os.stat(DATOTEKA_KSPOV).st_size == 0:
            self.igre = {}
            return

        with open(DATOTEKA_KSPOV, "r", encoding="utf-8") as vhodna:
            vsi_uporabniki = json.load(vhodna)

        if self.uporabnik in vsi_uporabniki:
            igre = vsi_uporabniki[self.uporabnik]
            self.igre = {
                int(id_igre): KamenSkarjePapirOgenjVoda(igralec, racunalnik)
                for id_igre, (igralec, racunalnik) in igre.items()
            }
        else:
            self.igre = {}
    
    def insert_game_kspov(self, game_id, player_score, computer_score) -> int:
        """
        Send an UPSERT request to the data/history microservice.
        Returns the number of affected rows reported by the service.
        """
        url = f"{DATA_URL}/data/kspov/insert"
        payload = {
            "username": self.uporabnik,
            "game_id": game_id,
            "player": player_score,
            "computer": computer_score,
        }

        try:
            r = requests.post(
                url,
                json=payload,
                timeout=(3, 10),  # 3s connect, 10s read
                headers={"Content-Type": "application/json"},
            )
            r.raise_for_status()
            data = r.json() if r.headers.get("content-type","").startswith("application/json") else {}
            return int(data.get("affected", 1))
        except requests.RequestException as e:
            raise RuntimeError(f"insert_game_kspov failed: {e}")

    def get_id_kspov(self):
        """
        Ask the Data microservice for a new game id and set it on this instance.
        Expects JSON like: {"id": 123} (also accepts "game_id" or "next_id").
        """
        url = f"{DATA_URL}/data/kspov/get/id"
        try:
            # If your service needs the username, send it along:
            r = requests.get(url, params={"username": self.uporabnik}, timeout=(2, 6))
            r.raise_for_status()
            payload = r.json() or {}

            # Accept common key names
            new_id = (payload.get("game_id"))
            if new_id is None:
                raise ValueError(f"Missing 'id' in response: {payload}")

            self.nastavi_id(int(new_id))
        except Exception as e:
            # Log + safe fallback
            print(f"[get_id_kspov] fetch from {url} failed: {e}", flush=True)
            self.nastavi_id(0)

#pomembno je da beležim rezultat igre in sicer to lahko shranim v datoteko kot {id_igre: [igralec, racunalnik]



        