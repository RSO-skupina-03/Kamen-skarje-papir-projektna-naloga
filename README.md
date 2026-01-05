# RPS — Microservices Web App (Rock–Paper–Scissors & Rock–Paper–Scissors–Fire–Water)

KŠP is a microservices-based web application for playing:
- **Rock–Paper–Scissors (RPS)**: winner is decided after **7** rounds
- **Rock–Paper–Scissors–Fire–Water (RPSFW)**: winner is decided after **15** rounds

The player plays against the computer. The system supports three user roles:
- **Guest** — basic gameplay
- **User** — basic gameplay
- **Subscriber** — authenticates via Google (OAuth2/OIDC) and can access game history

---

## 1. Architecture

### 1.1 Services
| Service | Repo folder | Host (local) | Docker Compose hostname | Responsibility |
|---|---|---:|---|---|
| Frontend, Session & API Gateway | `services/frontend` | `http://localhost:8080` | `http://frontend:8080` | UI, cookies/sessions, routes/proxies requests to backend services |
| Game Engine | `services/game_engine` | `http://localhost:8081` | `http://game_engine:8081` | Game logic, reads/writes game state in Redis |
| Authentication | `services/auth` | `http://localhost:8082` | `http://auth:8082` | Google OAuth2/OIDC integration, token validation, one-time ticket flow |
| Data Service | `services/data` | `http://localhost:8083` | `http://data:8083` | Persistent storage + queries (PostgreSQL/Neon) |

### 1.2 External dependencies
- **Redis** — short-term game state storage
- **PostgreSQL (Neon)** — persistent storage of game history
- **Google Auth Platform** — OAuth2/OIDC provider for subscribers

### 1.3 Diagram
<p align="center">
  <img src="arhi.png" alt="Arhitekturna shema mikro storitev" width="70%">
</p>

## 2. Health & Readiness

All microservices expose:

- `GET /health` — **liveness** (service process is running)
- `GET /ready` — **readiness** (service is ready to serve traffic; checks required environment variables and dependencies, e.g., Redis availability)

---

## 3. Tech Stack

- **Backend:** Python 3.11+, **Gunicorn** (WSGI server) + **Bottle** (web framework)
- **Databases:** **PostgreSQL** (persistent), **Redis** (short-term state / sessions)
- **Containers:** **Docker**, **Docker Compose**
- **Orchestration:** **Kubernetes** (planned / optional)
- **Communication:** **REST API**
- **Authentication:** **OAuth 2.0 / OIDC** (Google), **JWT** usage (where applicable)
- **CI/CD:** **GitHub Actions**
- **API Gateway:** Frontend service acts as API gateway (**Traefik/NGINX** optional/future)

## 4. Running the project

### 4.1 Prerequisites
- Docker + Docker Compose
- Google Auth Platform account
- Any PostgreSQL database provider (e.g., Neon)

### 4.2 Start

In the repository root, you must update `docker-compose.yaml` with your environment values for `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `SESSION_COOKIE_SECRET`, and `DB_URL`.

| Environment variable | Used by service(s) | What it represents | Example value |
|---|---|---|---|
| `GOOGLE_CLIENT_ID` | `auth` | Public identifier of your Google OAuth2/OIDC application (used to start the login flow). | `1234567890-abc123def456.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | `auth` | Secret key for your Google OAuth2/OIDC application (used to exchange the authorization code for tokens). | `GOCSPX-xxxxxxxxxxxxxxxxxxxx` |
| `SESSION_COOKIE_SECRET` | `frontend`, `auth` | Secret used to sign/encrypt session cookies so they can’t be forged/tampered with. | `change-this-to-a-long-random-string` |
| `DB_URL` | `data` | PostgreSQL connection string for Neon (or local Postgres). Used for persistent storage of game history. | `postgresql://user:pass@host:5432/dbname?sslmode=require` |

After updating the environment variables, you can run the web application locally with:

```bash
docker compose up --build
```

## 4.3 Verify Services

You can verify the health, readiness, and available endpoints of each microservice via Swagger UI:

```text
# Swagger UI for Frontend, Session & API Gateway Service
http://localhost:8080/docs

# Swagger UI for Game Engine Service
http://localhost:8081/docs

# Swagger UI for Authentication Service
http://localhost:8082/docs

# Swagger UI for Data Service
http://localhost:8083/docs
```

## 5. Branching Strategy
Due to small project there is only one `master` branch.
