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
  <img src="arhi.png" alt="Arhitekturna shema mikro storitev" width="100%">
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

## 4. Running Project Locally

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

## 5. Running Project on Microsoft Azure

The application is deployed to Microsoft Azure using Azure Kubernetes Service (AKS). All microservices are containerized with Docker and orchestrated via Kubernetes.

### 5.1 Prerequisites

1. **Azure CLI** installed and configured ([Installation Guide](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli))
2. **kubectl** installed ([Installation Guide](https://kubernetes.io/docs/tasks/tools/))
3. **Docker** installed and logged in to Docker Hub
4. **Azure subscription** with appropriate permissions
5. **Google Auth Platform** account with OAuth 2.0 credentials

### 5.2 Setup Azure Key Vault

Create and configure Azure Key Vault for storing secrets:

```bash
# Create resource group
az group create --name ksp-microservices --location swedencentral

# Create Key Vault
az keyvault create \
  --name ksp-kv-microservices \
  --resource-group ksp-microservices \
  --location swedencentral
```

### 5.3 Add Secrets to Key Vault

Add the required secrets to Key Vault:

```bash
# Session cookie secret (use a strong random string)
az keyvault secret set \
  --vault-name ksp-kv-microservices \
  --name session-cookie-secret \
  --value "your-strong-random-secret-key-here"

# Google OAuth Client ID (get from Google Cloud Console)
az keyvault secret set \
  --vault-name ksp-kv-microservices \
  --name google-client-id \
  --value "your-google-client-id.apps.googleusercontent.com"

# Google OAuth Client Secret (get from Google Cloud Console)
az keyvault secret set \
  --vault-name ksp-kv-microservices \
  --name google-client-secret \
  --value "your-google-client-secret"
```

### 5.4 Setup PostgreSQL Database

Create the PostgreSQL database for persistent storage:

```bash
# Create PostgreSQL Flexible Server
az postgres flexible-server create \
  --resource-group ksp-microservices \
  --name kspdb-microservices \
  --location swedencentral \
  --admin-user kspadminmicro \
  --admin-password "your-secure-password" \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --version 14 \
  --storage-size 32 \
  --public-access 0.0.0.0

# Create database
az postgres flexible-server db create \
  --resource-group ksp-microservices \
  --server-name kspdb-microservices \
  --database-name kspdb-microservices

# Get connection string
az postgres flexible-server show \
  --resource-group ksp-microservices \
  --name kspdb-microservices \
  --query fullyQualifiedDomainName -o tsv
```

After PostgreSQL is set up, add the database connection string to Key Vault:

```bash
az keyvault secret set \
  --vault-name ksp-kv-microservices \
  --name db-url \
  --value "postgresql://kspadminmicro:your-password@kspdb-microservices.postgres.database.azure.com:5432/kspdb-microservices"
```

### 5.5 Create AKS Cluster

Create Azure Kubernetes Service cluster:

```bash
# Create AKS cluster
az aks create \
  --resource-group ksp-microservices \
  --name ksp-aks-cluster-microservices \
  --location swedencentral \
  --node-count 1 \
  --node-vm-size Standard_B2s \
  --enable-managed-identity

# Get AKS credentials
az aks get-credentials \
  --resource-group ksp-microservices \
  --name ksp-aks-cluster-microservices \
  --overwrite-existing
```

### 5.6 Install Secrets Store CSI Driver

Install Secrets Store CSI Driver and Azure Key Vault Provider for secure secret management:

```bash
# Install Secrets Store CSI Driver
helm repo add secrets-store-csi-driver https://kubernetes-sigs.github.io/secrets-store-csi-driver/charts
helm install csi-secrets-store secrets-store-csi-driver/secrets-store-csi-driver \
  --namespace kube-system

# Install Azure Key Vault Provider
kubectl apply -f https://raw.githubusercontent.com/Azure/secrets-store-csi-driver-provider-azure/master/deployment/provider-azure-installer.yaml
```

### 5.7 Configure Key Vault Access

Grant AKS managed identity access to Key Vault:

```bash
# Get AKS managed identity client ID
AKS_IDENTITY_CLIENT_ID=$(az aks show \
  --resource-group ksp-microservices \
  --name ksp-aks-cluster-microservices \
  --query identityProfile.kubeletidentity.clientId -o tsv)

# Grant Key Vault access
az keyvault set-policy \
  --name ksp-kv-microservices \
  --object-id $AKS_IDENTITY_CLIENT_ID \
  --secret-permissions get list
```

### 5.8 Deploy Microservices

Deploy all microservices to AKS:

```bash
# Apply SecretProviderClass
kubectl apply -f k8s/secret-provider-class-microservices.yaml

# Deploy Redis (Frontend)
kubectl apply -f k8s/redis/deployment.yaml
kubectl apply -f k8s/redis/service.yaml

# Deploy Redis (Game Engine)
kubectl apply -f k8s/redis-game-engine/deployment.yaml
kubectl apply -f k8s/redis-game-engine/service.yaml

# Deploy microservices
kubectl apply -f k8s/auth/deployment.yaml
kubectl apply -f k8s/auth/service.yaml
kubectl apply -f k8s/game_engine/deployment.yaml
kubectl apply -f k8s/game_engine/service.yaml
kubectl apply -f k8s/data/deployment.yaml
kubectl apply -f k8s/data/service.yaml
kubectl apply -f k8s/frontend/deployment.yaml
kubectl apply -f k8s/frontend/service.yaml
```

### 5.9 Install NGINX Ingress Controller

Install NGINX Ingress Controller for external access:

```bash
# Install NGINX Ingress Controller
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace

# Apply Ingress configuration
kubectl apply -f k8s/ingress/frontend-ingress.yaml
kubectl apply -f k8s/ingress/tcp-configmap.yaml
```

### 5.10 Configure Domain and DNS

After deployment, get the external IP address:

```bash
# Get Ingress Controller IP
kubectl get service ingress-nginx-controller -n ingress-nginx
```

Create DNS A record pointing to the LoadBalancer IP address. Update Google OAuth redirect URI to match your domain (e.g., `http://your-domain.com:8082/auth/google/callback`).

### 5.11 Verify Deployment

Check that all pods are running:

```bash
kubectl get pods -l 'app in (ksp-redis-frontend,ksp-redis-game-engine,ksp-auth,ksp-frontend,ksp-game-engine,ksp-data)'
```

All pods should be in `Running` state.

## 6. Verify Services

### 6.1 Local Deployment (Docker Compose)

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

### 6.2 Cloud Deployment (Azure AKS)

For cloud deployment, replace `localhost` with your domain name or Ingress Controller IP:

```text
# Swagger UI for Frontend, Session & API Gateway Service
http://your-domain.com/docs
# or
http://<ingress-ip>/docs

# Swagger UI for Game Engine Service
http://your-domain.com:8081/docs
# or
http://<ingress-ip>:8081/docs

# Swagger UI for Authentication Service
http://your-domain.com:8082/docs
# or
http://<ingress-ip>:8082/docs

# Swagger UI for Data Service
http://your-domain.com:8083/docs
# or
http://<ingress-ip>:8083/docs
```

**Note:** For cloud deployment, you may need to configure port forwarding or use Ingress rules to access internal services. The frontend service is accessible via Ingress Controller on port 80, while other services may require direct access or port forwarding.

To check service status in Kubernetes:

```bash
# Get all pods
kubectl get pods

# Get services
kubectl get services

# Check pod logs
kubectl logs -f deployment/ksp-frontend
kubectl logs -f deployment/ksp-game-engine
kubectl logs -f deployment/ksp-auth
kubectl logs -f deployment/ksp-data
```

## 7. Branching Strategy

Due to small project there is only one `master` branch.
