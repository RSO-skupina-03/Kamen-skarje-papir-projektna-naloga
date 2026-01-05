# Tehnična dokumentacija (Kamen–Škarje–Papir)

## 1. Pregled
**KŠP** je spletna aplikacija za igranje iger *Kamen–Škarje–Papir* in *Kamen–Škarje–Papir–Ogenj–Voda*. Zmagovalec igre *Kamen–Škarje–Papir* se določi po sedmih odigranih partijah, zmagovalec igre *Kamen–Škarje–Papir–Ogenj–Voda* pa po petnajstih odigranih partijah. Igralec igra proti računalniku. Spletna aplikacija podpira tri tipe uporabnikov:
- Gost,
- Uporabnik,
- Naročnik.

Gost in uporabnik imata dostop do osnovnih funkcionalnosti spletne aplikacije. Naročnik se mora identificirati prek *Google Auth Platform* in ima poleg osnovnih funkcionalnosti na voljo tudi pregled zgodovine odigranih iger. Sistem podpira:
- prijavo uporabnika (npr. e-mail/username),
- ustvarjanje novih iger,
- izvajanje potez in posodabljanje rezultata,
- shranjevanje stanja igre v podatkovni bazi **Redis** (kratkoročno, z iztekom),
- trajno shranjevanje rezultatov iger v podatkovni bazi.


---

## 2. Uporabljena tehnologija

- **Backend:** Python 3.11+, spletni strežnik Gunicorn in Bottle spletno ogrodje
- **Baze podatkov:** PostgreSQL (trajno shranjevanje), Redis (seje)
- **Vsebniki:** Docker, Docker Compose
- **Orkestracija:** Kubernetes
- **Komunikacija:** REST API
- **Avtentikacija:** JWT, OAuth 2.0 integracija
- **CI/CD:** GitHub Actions
- **API Gateway:** Traefik/NGINX

## 3. Postavitev v oblaku

## 4. Arhitektura sistema
Sistem je sestavljen iz štirih mikrostoritev. Vsaka mikrostoritev ima poti `/health` in `/ready`, ki podajata informacijo o stanju storitve.

Pot `/health` je namenjena preverjanju, ali mikrostoritev deluje (liveness). Pot `/ready` pa prikazuje, ali je mikrostoritev pripravljena na obdelavo zahtevkov (readiness): preveri prisotnost zahtevanih okoljskih spremenljivk ter razpoložljivost odvisnosti, na primer Redisa.

### 4.1 Pregled mikrostoritev
Sistem je sestavljen iz naslednjih komponent:

- **Frontend, Session, API Gateway Service**: uporabniški vmesnik (HTTP), upravljanje sej in piškotkov ter vloga API prehoda (usmerjanje zahtevkov na zaledne storitve).
- **Game Engine Service**: poslovna logika za igranje iger *Kamen–Škarje–Papir* in *Kamen–Škarje–Papir–Ogenj–Voda* (ustvarjanje igre, izvedba poteze, izračun rezultata, upravljanje stanja igre).
- **Data Service**: dostop do podatkovne baze. Obe igri imata ločeno tabelo v podatkovni bazi
- **Authentication Service**: upravljanje prijave uporabnikov (OAuth2/OIDC tok, izmenjava/verifikacija žetonov).
- **Redis**: kratkoročno shranjevanje stanja aktivnih iger (TTL 15 min).
- **Neon Database (PostgreSQL)**: trajno shranjevanje podatkov o zgodovini iger.
- **Google Auth Platform**: ponudnik avtentikacije prek OAuth2/OIDC (upravljanje uporabniških računov in izdaja identitetnih žetonov).
- 

#### 4.1.1 Frontend, Session, API Gateway Service
- **Ime mikrostoritve v repozitoriju:** `frontend`
- **Host/port:** `http://localhost:8080`
- **Vloga:** uporabniški vmesnik + API prehod + upravljanje sej (piškotki)
- **Glavne poti:**
  - `GET /` – prikaz strani za prijavo uporabnika
  - `PUT /frontend/login` – prijava uporabnika (*Gost* ali *Uporabnik*) in nastavitev piškotkov
  - `GET /auth/finalize` – klic mikrostoritve *Authentication Service* za dokončanje avtentikacije naročnika preko *Google Auth Platform* in nastavitev piškotkov
  - `GET /igra` – prikaz začetnega menija za igranje iger *Kamen–Škarje–Papir* in *Kamen–Škarje–Papir–Ogenj–Voda*
  
  - `POST /ksp` — pridobi podatke o uporabnikovi izbiri (kamen, škarje ali papir) in jih posreduje mikrostoritvi *Game Engine*
  - `GET /ksp` — iz piškotkov prebere podatke o uporabniku, pridobi stanje igre (klic mikrostoritve *Game Engine*) in prikaže igro
  - `GET /nova_igra_ksp` — inicializacija nove igre *Kamen–Škarje–Papir*
  - `GET /zgodovina_ksp` — pridobi podatke o zgodovini iger *Kamen–Škarje–Papir* (klic mikrostoritve *Data Service*) in prikaže zgodovino
  - `DELETE /brisi_ksp` — izbriše zgodovino iger *Kamen–Škarje–Papir* (klic mikrostoritve *Data Service*) 
  
  - `POST /kspov` — pridobi podatke o uporabnikovi izbiri (kamen, škarje, papir, ogenj ali voda) in jih posreduje mikrostoritvi *Game Engine*
  - `GET /kspov` — iz piškotkov prebere podatke o uporabniku, pridobi stanje igre (klic mikrostoritve *Game Engine*) in prikaže igro
  - `GET /nova_igra_kspov` — inicializacija nove igre *Kamen–Škarje–Papir–Ogenj–Voda*
  - `GET /zgodovina_kspov` — pridobi podatke o zgodovini iger *Kamen–Škarje–Papir–Ogenj–Voda* (klic mikrostoritve *Data Service*) in prikaže zgodovino
  - `DELETE /brisi_kspov` — izbriše zgodovino iger *Kamen–Škarje–Papir–Ogenj–Voda* (klic mikrostoritve *Data Service*)
- **Odvisnosti:** *Game Engine Service*, *Authentication Service*, *Data Service*

#### 4.1.2 Game Engine Service
- **Ime mikrostoritve v repozitoriju:** `game_engine`
- **Host/port:** `http://localhost:8081`  
  *(znotraj Docker Compose: `http://game_engine:8081`)*
- **Vloga:** izvajanje logike igre in shranjevanje stanja v Redis
- **Glavne poti:**
  - `POST /game/ksp/nova` – inicializira novo igro *Kamen–Škarje–Papir*
  - `GET /game/ksp/state` – vrne trenutno stanje igre *Kamen–Škarje–Papir*
  - `POST /game/ksp/poteza` – izvede potezo in izračuna novo stanje igre *Kamen–Škarje–Papir*
  
  - `POST /game/kspov/nova` – inicializira novo igro *Kamen–Škarje–Papir–Ogenj–Voda*
  - `GET /game/kspov/state` – vrne trenutno stanje igre *Kamen–Škarje–Papir–Ogenj–Voda*
  - `POST /game/kspov/poteza` – izvede potezo in izračuna novo stanje igre *Kamen–Škarje–Papir–Ogenj–Voda*
- **Odvisnosti:** *Redis*, *Data Service*

#### 4.1.4 Authentication Service
- **Ime mikrostoritve v repozitoriju:** `auth`
- **Host/port:** `http://localhost:8082`  
  *(znotraj Docker Compose: `http://auth:8082`)*
- **Vloga:** integracija OAuth2/OIDC (Google) in validacija ID žetonov
- **Glavne poti:**
  - `GET /auth/google/login` – preusmeritev uporabnika na *Google Auth Platform*
  - `GET /auth/google/callback` – obdelava povratnega klica (*callback*) iz *Google Auth Platform*, generiranje enkratne vstopnice ter posredovanje podatkov mikrostoritvi *Frontend, Session, API Gateway*
  - `GET /auth/redeem` – vrne podatke o prijavljenem uporabniku na podlagi vstopnice
- **Odvisnosti:** *Google Auth Platform*

#### 4.1.3 Data Service
- **Ime mikrostoritve v repozitoriju:** `data`
- **Host/port:** `http://localhost:8083`  
  *(znotraj Docker Compose: `http://data:8083`)*
- **Vloga:** trajno shranjevanje podatkov in izvajanje poizvedb nad podatkovno bazo
- **Glavne poti:**
  - `POST /data/ksp/insert` – zapiše končni rezultat igre *Kamen–Škarje–Papir* v podatkovno bazo
  - `GET /data/ksp/get/id` – pridobi ustrezen identifikator igre
  - `GET /data/ksp/history` – vrne zgodovino iger uporabnika
  - `POST /data/ksp/delete` – izbriše zgodovino iger uporabnika

  - `POST /data/kspov/insert` – zapiše končni rezultat igre *Kamen–Škarje–Papir–Ogenj–Voda* v podatkovno bazo
  - `GET /data/kspov/get/id` – pridobi ustrezen identifikator igre
  - `GET /data/kspov/history` – vrne zgodovino iger uporabnika
  - `POST /data/kspov/delete` – izbriše zgodovino iger uporabnika
- **Odvisnosti:** *Neon Database (PostgreSQL)*`

<div style="page-break-after: always;"></div>

### 3.2 Shema arhitekture
<p align="center">
  <img src="arhi.png" alt="Arhitekturna shema mikro storitev" width="80%">
</p>


