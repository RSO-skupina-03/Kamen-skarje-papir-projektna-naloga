# KSP – Tehnična dokumentacija (Kamen–Škarje–Papir)

## 1. Pregled
**KSP** je spletna aplikacija za igranje igre Kamen–Škarje–Papir in Kamen-Škarje-Papir-Ogenj-Voda. Sistem podpira:
- prijavo/uporabnika (npr. e-mail/username),
- ustvarjanje novih iger,
- izvajanje potez in posodabljanje rezultata,
- shranjevanje stanja igre v podatkovni bazi **Redis** (kratkoročno, z iztekom),
- trajno shranjevanje iger v podatkovni bazi.

---

## 2. Arhitektura sistema

### 2.1 Pregled mikrostoritev
Sistem je sestavljen iz naslednjih komponent:

- **Frontend, Session & API Gateway Service**: uporabniški vmesnik (HTTP), upravljanje sej in piškotkov ter vloga API prehoda (usmerjanje zahtevkov na zaledne storitve).
- **Game Engine Service**: poslovna logika za igranje iger *Kamen–Škarje–Papir* in *Kamen–Škarje–Papir–Ogenj–Voda* (ustvarjanje igre, izvedba poteze, izračun rezultata, upravljanje stanja igre).
- **Data Service**: dostop do podatkovne baze (CRUD nad zgodovino iger, generiranje identifikatorjev, poizvedbe zgodovine).
- **Authentication Service**: upravljanje prijave uporabnikov (OAuth2/OIDC tok, izmenjava/verifikacija žetonov, povezava seje z uporabnikom).
- **Redis**: kratkoročno shranjevanje stanja aktivnih iger (TTL 15 min).
- **Neon Database (PostgreSQL)**: trajno shranjevanje podatkov o zgodovini iger.
- **Google Auth Platform**: ponudnik avtentikacije prek OAuth2/OIDC (upravljanje uporabniških računov in izdaja identitetnih žetonov).
- 

#### 2.1.1 Frontend, Session & API Gateway Service
- **Ime storitve:** `frontend`
- **Host/port:** `http://localhost:8000`
- **Vloga:** UI + API prehod + upravljanje sej (piškotki)
- **Glavne poti:**
  - `GET /` – začetna stran
  - `GET /login` – začetek prijave
  - `GET /callback/google` – OAuth callback
  - `POST /api/ksp/new` → (proxy) `game_engine` `POST /game/ksp/new`
  - `POST /api/ksp/move` → (proxy) `game_engine` `POST /game/ksp/move`
  - `GET /api/ksp/history` → (proxy) `data` `GET /data/ksp/history?username=...`
- **Odvisnosti:** `game_engine`, `auth`

#### 2.1.2 Game Engine Service
- **Ime storitve:** `game_engine`
- **Host/port:** `http://localhost:8001`  
  *(znotraj Docker Compose: `http://game_engine:8001`)*
- **Vloga:** logika igre, upravljanje stanja v Redis
- **Glavne poti (primer):**
  - `POST /game/ksp/new` – ustvari novo igro, vrne `game_id`
  - `POST /game/ksp/move` – izvede potezo (npr. parameter `orozje`), posodobi stanje in sproži zapis v zgodovino
  - `GET /health`, `GET /ready`
- **Redis ključi (primer):**
  - `ksp:<username>:games` (HASH; TTL 15 min)
  - `ksp:<username>:next_id` (COUNTER; brez TTL)
- **Odvisnosti:** `redis`, `data` (HTTP ali RabbitMQ), `auth` (validacija)

#### 2.1.3 Data Service
- **Ime storitve:** `data`
- **Host/port:** `http://localhost:8083`  
  *(znotraj Docker Compose: `http://data:8083`)*
- **Vloga:** trajno shranjevanje in poizvedbe nad zgodovino
- **Glavne poti (primer):**
  - `POST /data/ksp/insert` – vnos/posodobitev igre v bazo
  - `GET /data/ksp/get/id?username=...` – pridobi nov/ustrezen `game_id`
  - `GET /data/ksp/history?username=...` – vrne zgodovino iger
  - `POST /data/ksp/delete` – pobriše podatke uporabnika
  - `GET /health`, `GET /ready`
- **Odvisnosti:** `Neon Postgres (DB_URL)`

#### 2.1.4 Authentication Service
- **Ime storitve:** `auth`
- **Host/port:** `http://localhost:8002`  
  *(znotraj Docker Compose: `http://auth:8002`)*
- **Vloga:** OAuth2/OIDC integracija (Google), validacija ID tokenov, povezava seje z uporabnikom
- **Glavne poti (primer):**
  - `GET /auth/login` – preusmeritev na Google
  - `GET /auth/callback` – obdelava callbacka
  - `GET /auth/me` – vrne prijavljenega uporabnika (seja/token)
- **Odvisnosti:** `Google Auth Platform`


### 2.2 Diagram (predlog)
**Predlog vsebine**: diagram (Mermaid/PlantUML) z tokovi:
- frontend → game_engine (HTTP)
- game_engine → redis (cache state)
- game_engine → rabbitmq (enqueue write)
- rabbitmq worker → data service/model (DB)
- game_engine → rabbitmq RPC (read) ali HTTP (read) – odvisno od implementacije

Primer Mermaid:
```mermaid
flowchart TB
  CL["Client"] -- HTTP --> FE["Frontend & Session & API Gateway Service"]

  FE -- HTTP --> GE["Game Engine Service"]
  FE -- HTTP --> AUTH["Authentication Service"]

  AUTH -- OAuth2/OIDC --> GOOGLE[("Google Auth Platform")]

  GE -- Redis HSET/HGET --> R[("Redis")]
  GE -- HTTP --> DA["Data Service"]

  DA -- SQL insert/get/delete --> DB[("Neon Database (PostgreSQL)")]


