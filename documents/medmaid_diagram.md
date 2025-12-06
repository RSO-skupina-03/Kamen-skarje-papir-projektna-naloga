---
config:
  layout: elk
---
flowchart TB
 subgraph subGraph0["Client Layer"]
        U["Uporabnik<br>Web Browser"]
  end
 subgraph subGraph1["API Gateway Layer"]
        GW["API Gateway<br>Traefik or NGINX<br>Load Balancing<br>SSL Termination<br>Rate Limiting<br>JWT Validation with tenant_id<br>Tenant Routing by subdomain or header"]
  end
 subgraph subGraph2["Auth Service"]
        AUTH["Auth Service<br>Python Hypercorn<br>OAuth 2.0 or OIDC per tenant<br>JWT Generation includes tenant_id<br>User Validation"]
  end
 subgraph subGraph3["Game Engine Service"]
        GAME["Game Engine<br>Python Hypercorn<br>KSP Logic<br>KSPOV Logic<br>Game Rules<br>Tenant Aware Processing"]
  end
 subgraph subGraph4["Session Service"]
        SESSION["Session Service<br>Python FastAPI<br>Game State<br>Redis Cache<br>Coordination<br>Tenant Namespacing"]
  end
 subgraph subGraph5["History Service"]
        HISTORY["History Service<br>Python Hypercorn<br>Game Results<br>Row Level Security by tenant_id"]
  end
 subgraph subGraph6["Privacy Services"]
        CONSENT["Consent and DSR Service<br>Consent records<br>Data Subject Requests export and delete"]
  end
 subgraph subGraph7["Microservices Layer"]
        subGraph2
        subGraph3
        subGraph4
        subGraph5
        subGraph6
  end
 subgraph subGraph8["External Services"]
        OAUTH["OAuth Provider<br>Google GitHub Microsoft<br>Per tenant config"]
        KMS["Key Management Vault or KMS<br>Per tenant data keys<br>Rotation policies"]
  end
 subgraph Databases["Databases"]
        REDIS[("Redis<br>Session Storage<br>Tenant namespace prefix<br>TTL Management")]
        POSTGRES[("PostgreSQL EU<br>Persistent Storage<br>User Game History<br>RLS by tenant_id<br>At Rest Encryption")]
  end
 subgraph subGraph10["Data Layer"]
        subGraph8
        Databases
  end
    U -- HTTPS REST --> GW
    GW -- HTTPS REST JWT with tenant_id --> AUTH
    GW -- HTTPS REST Tenant Routed --> SESSION & HISTORY
    SESSION -- HTTPS REST Game Logic --> GAME
    SESSION -- HTTPS REST Async Storage --> HISTORY
    AUTH -- OAuth or OIDC per tenant --> OAUTH
    AUTH -- Consent check --> CONSENT
    SESSION -- Consent or DSR check --> CONSENT
    HISTORY -- Consent or DSR check --> CONSENT
    SESSION -- Redis Protocol State with tenant prefix --> REDIS
    HISTORY -- SQL Protocol RLS by tenant_id --> POSTGRES
    AUTH -- Fetch keys --> KMS
    SESSION -- Encrypt secrets --> KMS
    HISTORY -- Encrypt or decrypt --> KMS
     U:::client
     GW:::gateway
     AUTH:::microservice
     GAME:::microservice
     SESSION:::microservice
     HISTORY:::microservice
     CONSENT:::privacy
     OAUTH:::external
     KMS:::external
     REDIS:::database
     POSTGRES:::database
    classDef client fill:#e1f5fe
    classDef gateway fill:#f3e5f5
    classDef microservice fill:#e8f5e8
    classDef database fill:#fff3e0
    classDef external fill:#fce4ec
    classDef privacy fill:#e0f7fa
