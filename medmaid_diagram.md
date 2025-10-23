graph TB
    subgraph "Client Layer"
        U[Uporabnik<br/>Web Browser]
    end
    
    subgraph "API Gateway Layer"
        GW[API Gateway<br/>Traefik/NGINX<br/>• Load Balancing<br/>• SSL Termination<br/>• Rate Limiting<br/>• JWT Validation]
    end
    
    subgraph "Microservices Layer"
        subgraph "Auth Service"
            AUTH[Auth Service<br/>Python Hypercorn<br/>• OAuth 2.0 Integration<br/>• JWT Generation<br/>• User Validation]
        end
        
        subgraph "Game Engine Service"
            GAME[Game Engine<br/>Python Hypercorn<br/>• KSP Logic<br/>• KSPOV Logic<br/>• Game Rules<br/>]
        end
        
        subgraph "Session Service"
            SESSION[Session Service<br/>Python FastAPI<br/>• Game State<br/>• Redis Cache<br/>• Coordinaton]
        end
        
        subgraph "History Service"
            HISTORY[History Service<br/>Python Hypercorn<br/>• Game Results]
        end
    end
    
    subgraph "Data Layer"
        subgraph "External Services"
            OAUTH[OAuth Provider<br/>Google/GitHub/Microsoft<br/>User Directory]
        end
        
        subgraph "Databases"
            REDIS[(Redis<br/>Session Storage<br/>• Game State<br/>• TTL Management)]
            POSTGRES[(PostgreSQL<br/>Persistent Storage<br/>• User Game History<br/>)]
        end
    end
    
    %% Client connections
    U -->|HTTPS/REST| GW
    
    %% API Gateway connections
    GW -->|HTTPS/REST<br/>JWT Validation| AUTH
    GW -->|HTTPS/REST<br/>Game Management| SESSION
    GW -->|HTTPS/REST<br/>History Access| HISTORY
    
    %% Inter-service communication
    SESSION -->|HTTPS/REST<br/>Game Logic| GAME
    SESSION -->|HTTPS/REST<br/>Async Storage| HISTORY
    AUTH -->|OAuth 2.0 Protocol<br/>User Auth| OAUTH
    
    %% Database connections
    SESSION -->|Redis Protocol<br/>State Storage| REDIS
    HISTORY -->|SQL Protocol<br/>Persistent Storage| POSTGRES
    
    %% Styling
    classDef client fill:#e1f5fe
    classDef gateway fill:#f3e5f5
    classDef microservice fill:#e8f5e8
    classDef database fill:#fff3e0
    classDef external fill:#fce4ec
    
    class U client
    class GW gateway
    class AUTH,GAME,SESSION,HISTORY microservice
    class REDIS,POSTGRES database
    class OAUTH external