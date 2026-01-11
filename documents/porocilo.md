# POROČILO - RSO SEMINAR 2025/2026

## Osnovni podatki

**Naslov projekta:** Predelava aplikacije Kamen-Škarje-Papir v Cloud Native Mikro Storitve

**Člani skupine:** Bernard Kučina, Filip Merkan

**Povezava do organizacije:** https://github.com/RSO-skupina-03

**Povezava do aplikacije:** http://kamen-skarje-papir.click

---

## Kratek opis projekta

Projekt predstavlja predelavo obstoječe monolitne aplikacije "Kamen-Škarje-Papir" ki je objavljena v [GitHub organizaciji](https://github.com/RSO-skupina-03) v sodobno cloud native arhitekturo z uporabo mikro storitev. Trenutna aplikacija, ki podpira dve različici igre (klasično KŠP in razširjeno KŠPOV z Ogenj/Voda), bo razdeljena na 4 neodvisnih mikro storitev, ki bodo omogočale boljšo skalabilnost, vzdrževanje in razširljivost. Rešitev bo rešila probleme monolitne arhitekture, kot so težko vzdrževanje, omejena skalabilnost in tesno povezanost komponent, ter zagotovila visoko dostopnost in odpornost na napake.

---

## Ogrodje in razvojno okolje

### Tehnologije in ogrodja:
- **Backend:** Python 3.11+, spletni strežnik Gunicorn in Bottle spletno ogrodje
- **Baze podatkov:** PostgreSQL (trajno shranjevanje), Redis (seje)
- **Vsebniki:** Docker, Docker Compose
- **Orkestracija:** Kubernetes
- **Komunikacija:** REST API
- **Avtentikacija:** JWT, OAuth 2.0 integracija
- **CI/CD:** GitHub Actions
- **API Gateway:** Traefik/NGINX

### Razvojno okolje
- **IDE:** Visual Studio Code  
- **Upravljanje različic:** Git, GitHub  
- **Testiranje API-jev:** Swagger UI  
- **Dokumentacija:** Swagger (OpenAPI), Markdown  

---

<div style="page-break-after: always;"></div>

## Shema arhitekture

<p align="center">
  <img src="arhi.png" alt="Arhitekturna shema mikro storitev" width="80%">
</p>


---

## Seznam funkcionalnosti mikrostoritev

### 1. Authentication Service
**Funkcionalnosti:**
- Integracija OAuth2/OIDC (Google) in validacija ID žetonov

**Glavne poti:**
  - `GET /auth/google/login` – preusmeritev uporabnika na *Google Auth Platform*
  - `GET /auth/google/callback` – obdelava povratnega klica (*callback*) iz *Google Auth Platform*, generiranje enkratne vstopnice ter posredovanje podatkov mikrostoritvi *Frontend, Session, API Gateway*
  - `GET /auth/redeem` – vrne podatke o prijavljenem uporabniku na podlagi vstopnice

### 2. Game Engine Service
**Funkcionalnosti:**
- Implementacija igralne logike za KŠP, zmagovalec določen po sedmih igrah
- Implementacija igralne logike za KŠPOV, zmagovalec določen po petnajstih igrah
- Shranjevanje stanja v trenurne igre na Redis
  
**Glavne poti:**
  - `POST /game/ksp/nova` – inicializira novo igro *Kamen–Škarje–Papir*
  - `GET /game/ksp/state` – vrne trenutno stanje igre *Kamen–Škarje–Papir*
  - `POST /game/ksp/poteza` – izvede potezo in izračuna novo stanje igre *Kamen–Škarje–Papir*
  
  - `POST /game/kspov/nova` – inicializira novo igro *Kamen–Škarje–Papir–Ogenj–Voda*
  - `GET /game/kspov/state` – vrne trenutno stanje igre *Kamen–Škarje–Papir–Ogenj–Voda*
  - `POST /game/kspov/poteza` – izvede potezo in izračuna novo stanje igre *Kamen–Škarje–Papir–Ogenj–Voda*

### 4. Data Service
**Funkcionalnosti:**
- Shranjevanje zaključenih iger (PostgreSQL)
- Pregled zgodovine iger
- Brisanje zgodovine

**Glavne poti:**
  - `POST /data/ksp/insert` – zapiše končni rezultat igre *Kamen–Škarje–Papir* v podatkovno bazo
  - `GET /data/ksp/get/id` – pridobi ustrezen identifikator igre
  - `GET /data/ksp/history` – vrne zgodovino iger uporabnika
  - `POST /data/ksp/delete` – izbriše zgodovino iger uporabnika

  - `POST /data/kspov/insert` – zapiše končni rezultat igre *Kamen–Škarje–Papir–Ogenj–Voda* v podatkovno bazo
  - `GET /data/kspov/get/id` – pridobi ustrezen identifikator igre
  - `GET /data/kspov/history` – vrne zgodovino iger uporabnika
  - `POST /data/kspov/delete` – izbriše zgodovino iger uporabnika

### 5. Frontend, Session, API Gateway Service
**Funkcionalnosti:**
- Usmerjanje zahtev na mikrostoritve
- Prikaz uporabniškega vmesnika (HTML/CSS/JS)
- Upravljanje sej (piškotki)
- Omejevanje hitrosti zahtevkov (rate limiting)
- Porazdeljevanje bremena med mikrosotiravmi (load balancing)

**Glavne poti:**
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

---

## Primeri uporabe

### Osnovni primeri uporabe:

1. **Prijava naročnika**
   - Naročnik dostopa do aplikacije prek domene http://kamen-skarje-papir.click.
   - Naročnik klikne gumb "Prijava Google"
   - Sistem preusmeri na OAuth provider
   - OAuth provider vrne avtentikacijsko kodo
   - Naročnik je preusmerjen na začetni meni
  
2. **Prijava uporabika**
   - Uporabnik dostopa do aplikacije prek domene http://kamen-skarje-papir.click.
   - Uporabnik vpiše svoje uporabiško ime
   - Uporabnik klikne gumb "Prijava"
  
3. **Prijava Gosta**
   - Uporabnik dostopa do aplikacije prek domene http://kamen-skarje-papir.click.
   - Uporabnik klikne gumb "Gost"

4. **Nova igra KŠP**
   - Uporabnik/Gost/Naročnik klikne gumb "KŠP"
   - Prikaže se igralna konzola za igro KŠP
   - Ob pritisku na gumb Game Engine Service ustavri novo instanco igre KŠP

5. **Nova igra KŠPOV**
   - Uporabnik/Gost/Naročnik klikne gumb "KŠPOV"
   - Prikaže se igralna konzola za igro KŠPOV
   - Ob pritisku na gumb Game Engine Service ustavri novo instanco igre KŠPOV

6. **Igra poteze KSP**
   - Uporabnik/Gost/Naročnik izbere možnost (Kamen/Škarje/Papir)
   - Game Engine Service izračuna rezultat
   - Session Service posodobi stanje igre v okviru izbranega `tenant_id`

7. **Igra poteze KSPOV**
   - Uporabnik izbere orožje (Kamen/Škarje/Papir/Ogenj/Voda)
   - Game Engine izračuna rezultat z razširjenimi pravili
   - Session Service posodobi stanje igre v okviru izbranega `tenant_id`

8. **Pregled zgodovine KSP**
   - Uporabnik zahteva zgodovino KSP iger
   - History Service vrne shranjene rezultate filtrirane po `tenant_id`
   - Sistem prikaže statistike

9.  **Pregled zgodovine KSPOV**
   - Uporabnik zahteva zgodovino KSPOV iger
   - History Service vrne shranjene rezultate filtrirane po `tenant_id`
   - Sistem prikaže statistike

10. **Brisanje zgodovine**
   - Uporabnik zahteva brisanje zgodovine
   - History Service počisti podatke iz PostgreSQL z uveljavljeno RLS po `tenant_id`
   - Sistem potrdi uspešno brisanje

11. **Odjava uporabnika**
   - Uporabnik se odjavi iz sistema
   - Auth Service invalidira JWT token
   - Sistem preusmeri na OAuth provider za odjavo
   - Sistem preusmeri na prijavo

### Multi-tenant primer uporabe - Prijava in igranje v okviru najemnika

**Udeleženci:** Uporabnik, API Gateway, Auth Service, Session Service, Game Engine, History Service

**Tok:**
1. Uporabnik odpre `acme.example.com` (ali pošlje `X-Tenant-ID: acme`).
2. API Gateway zabeleži `tenant_id` in doda ga v posredovane zahteve.
3. Uporabnik se prijavi prek OAuth; Auth Service izda JWT, ki vsebuje `tenant_id`.
4. Uporabnik ustvari novo KSPOV igro; Session Service ustvari sejo v Redis pod imenom prostora `tenant:acme:*`.
5. Uporabnik odigra poteze; Session Service kliče Game Engine, posodablja stanje v okviru `tenant_id`.
6. Po zaključku igre Session Service pošlje rezultat v History Service; v PostgreSQL je uveljavljena RLS po `tenant_id`.
7. Uporabnik pregleda zgodovino; vrnejo se samo rezultati z `tenant_id = acme`.

### Kompleksnejši primer uporabe - Zaključek igre s shranjevanjem:

**Udeleženci:** Uporabnik, Session Service, Game Engine, History Service, Auth Service

**Tok:**
1. Uporabnik igra zadnjo potezo v KSPOV igri (15. poteza)
2. Session Service pošlje potezo v Game Engine
3. Game Engine vrne rezultat z oznako `isFinished: true`
4. Session Service shrani končno stanje v Redis
5. Session Service asinhrono pošlje rezultat v History Service
6. History Service shrani rezultat v PostgreSQL
7. Session Service počisti igro iz Redis
8. Uporabnik vidi končni rezultat in statistike

**Komunikacije:**
- Session → Game Engine (HTTP): `POST /game/kspov/play`
- Session → History (HTTP): `POST /history/ingest`
- UI → Session (HTTP): `POST /sessions/{id}/move`

