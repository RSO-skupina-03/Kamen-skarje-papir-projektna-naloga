import os, json, requests, redis
from random import randint
from dotenv import load_dotenv

load_dotenv()
MOZNOSTI = ['Kamen', 'Škarje', 'Papir']
MOZNOSTI_2 = ['Kamen', 'Škarje', 'Papir', 'Voda', 'Ogenj']
ZACETEK = 'Zacetek'

DATA_URL = os.environ["DATA_URL"]

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

        self.redis = redis.Redis(
            host=os.environ["REDIS_HOST"],
            port=int(os.environ["REDIS_PORT"]),
            db=int(os.environ["REDIS_DB"]),
            decode_responses=True,
        )

        # print("REDIS:", self.redis.connection_pool.connection_kwargs)
        # print("PING:", self.redis.ping())

    def nastavi_uporabnika(self, uporabnik):
        self.uporabnik = uporabnik

    def _ensure_user(self):
        if not self.uporabnik:
            raise ValueError("Uporabnik ni nastavljen. Pokliči nastavi_uporabnika(uporabnik).")

    def prosti_id_igre(self):
        self._ensure_user()

        if not hasattr(self, "_next_id_key"):
            # fallback if someone uses Datoteka directly
            self.id += 1
            return self.id

        new_id = int(self.redis.incr(self._next_id_key()))
        self.id = new_id
        return new_id

    def nastavi_id(self, id):
        self._ensure_user()
        self.id = int(id)

        if hasattr(self, "_next_id_key"):
            self.redis.set(self._next_id_key(), str(self.id))


#============================================================================================================================================================
   
class KSP(Datoteka):
    # Keys live ONLY here (as you want)
    def _games_key(self) -> str:
        self._ensure_user()
        return f"ksp:{self.uporabnik}:games"

    def _next_id_key(self) -> str:
        self._ensure_user()
        return f"ksp:{self.uporabnik}:next_id"

    def nova_igra(self):
        self.preberi_iz_datoteke()
        nov_id = self.prosti_id_igre()

        sveza_igra = nova_igra()  # your existing factory
        self.igre[nov_id] = sveza_igra

        self.shrani_v_datoteko()
        return nov_id

    def potek_igre(self, id_igre, orozje):
        self.preberi_iz_datoteke()

        if id_igre not in self.igre:
            raise KeyError(f"Igra z id={id_igre} ne obstaja za uporabnika {self.uporabnik}")

        trenutna_igra = self.igre[id_igre]
        trenutna_igra.potek_igre(orozje)
        self.igre[id_igre] = trenutna_igra

        self.shrani_v_datoteko()

    def shrani_v_datoteko(self):
        key = self._games_key()

        mapping = {
        str(id_igre): json.dumps([int(igra.igralec), int(igra.racunalnik)], ensure_ascii=False)
        for id_igre, igra in self.igre.items()
        }

        pipe = self.redis.pipeline()

        if not mapping:
            pipe.delete(key)
            pipe.execute()
            return
        
        pipe.hset(key, mapping=mapping)
        pipe.expire(key, 15 * 60)
        pipe.execute()

    def preberi_iz_datoteke(self):
        key = self._games_key() 
        igre_map = self.redis.hgetall(key)

        if not igre_map:
            self.igre = {}
            return

        self.igre = {}
        for id_igre_str, raw in igre_map.items():
            igralec, racunalnik = json.loads(raw)
            self.igre[int(id_igre_str)] = KamenSkarjePapir(int(igralec), int(racunalnik))

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
        
    def get_id_ksp(self) -> int:
        url = f"{DATA_URL}/data/ksp/get/id"
        r = requests.get(url, params={"username": self.uporabnik}, timeout=(2, 6))
        r.raise_for_status()
        payload = r.json() or {}

        counter_key = self._next_id_key()

        # treat payload["game_id"] as MAX used id (allows 0)
        if "game_id" not in payload or payload["game_id"] is None:
            raise ValueError(f"Missing game_id in response: {payload}")

        db_max = int(payload["game_id"])   # max used id in DB
        new_id = db_max + 1                # next id to use

        # Sync Redis counter to at least db_max (NOT new_id)
        curr = int(self.redis.get(counter_key) or 0)
        if curr < db_max:
            self.redis.set(counter_key, str(db_max))

        # Set local id to the id we will use
        self.nastavi_id(new_id)
        return new_id
#=========================================================================================================================================================

class KSPOV(Datoteka):

    def _games_key(self) -> str:
        self._ensure_user()
        return f"kspov:{self.uporabnik}:games"

    def _next_id_key(self) -> str:
        self._ensure_user()
        return f"kspov:{self.uporabnik}:next_id"

    def nova_igra_1(self):
        self.preberi_iz_datoteke()
        nov_id = self.prosti_id_igre()

        sveza_igra = nova_igra_1()  # your existing factory
        self.igre[nov_id] = sveza_igra

        self.shrani_v_datoteko()
        return nov_id

    def potek_igre_1(self, id_igre, orozje):
        self.preberi_iz_datoteke()
        trenutna_igra = self.igre[id_igre]

        trenutna_igra.potek_igre_1(orozje)
        self.igre[id_igre] = trenutna_igra

        self.shrani_v_datoteko()


    def potek_igre(self, id_igre, orozje):
        self.preberi_iz_datoteke()

        if id_igre not in self.igre:
            raise KeyError(f"Igra z id={id_igre} ne obstaja za uporabnika {self.uporabnik}")

        trenutna_igra = self.igre[id_igre]
        trenutna_igra.potek_igre(orozje)
        self.igre[id_igre] = trenutna_igra

        self.shrani_v_datoteko()

    def shrani_v_datoteko(self):
        mapping = {
            str(id_igre): json.dumps([int(igra.igralec), int(igra.racunalnik)], ensure_ascii=False)
            for id_igre, igra in self.igre.items()
        }

        key = self._games_key()
        pipe = self.redis.pipeline()

        pipe.delete(key)
        if mapping:
            pipe.hset(key, mapping=mapping)
            pipe.expire(key, 15 * 60)  # 15 minutes

        pipe.execute()

    def preberi_iz_datoteke(self):
        key = self._games_key() 
        igre_map = self.redis.hgetall(key)

        if not igre_map:
            self.igre = {}
            return

        self.igre = {}
        for id_igre_str, raw in igre_map.items():
            igralec, racunalnik = json.loads(raw)
            self.igre[int(id_igre_str)] = KamenSkarjePapirOgenjVoda(int(igralec), int(racunalnik))
    
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

    def get_id_kspov(self) -> int:
        url = f"{DATA_URL}/data/kspov/get/id"
        r = requests.get(url, params={"username": self.uporabnik}, timeout=(2, 6))
        r.raise_for_status()
        payload = r.json() or {}

        counter_key = self._next_id_key()

        # treat payload["game_id"] as MAX used id (allows 0)
        if "game_id" not in payload or payload["game_id"] is None:
            raise ValueError(f"Missing game_id in response: {payload}")

        db_max = int(payload["game_id"])   # max used id in DB
        new_id = db_max + 1                # next id to use

        # Sync Redis counter to at least db_max (NOT new_id)
        curr = int(self.redis.get(counter_key) or 0)
        if curr < db_max:
            self.redis.set(counter_key, str(db_max))

        # Set local id to the id we will use
        self.nastavi_id(new_id)
        return new_id

#pomembno je da beležim rezultat igre in sicer to lahko shranim v datoteko kot {id_igre: [igralec, racunalnik]



        