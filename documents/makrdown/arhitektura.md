---
config:
  layout: elk
---
flowchart TB
    CL["Client<br/>(Uporabnik)"] -- HTTP/HTTPS<br/>port 80 --> ING["NGINX Ingress Controller<br/>(LoadBalancer)"]
    ING -- HTTP<br/>port 8080 --> FE["Frontend & Session &<br/>API Gateway Service"]
    ING -- TCP passthrough<br/>port 8082 --> AUTH["Authentication Service"]
    
    FE -- HTTP<br/>port 8081 --> GE["Game Engine Service"]
    FE -- HTTP<br/>port 8082 --> AUTH
    FE -- HTTP<br/>port 8083 --> DA["Data Service"]
    FE -- Redis ZADD/ZCARD/INCR/LPUSH --> RF[("Redis<br/>(Frontend)<br/>Rate Limiting, Metrics")]
    
    AUTH -- OAuth2/OIDC --> GOOGLE[("Google Auth<br/>Platform")]
    
    GE -- Redis HSET/HGETALL --> RG[("Redis<br/>(Game Engine)<br/>Game State")]
    GE -- HTTP<br/>port 8083 --> DA
    
    DA -- SQL<br/>insert/get/delete --> DB[("PostgreSQL<br/>(Azure Flexible Server)")]
    
    KV[("Azure Key Vault<br/>Secrets Management")] -.->|Secrets Store<br/>CSI Driver<br/>Volume Mount| FE
    KV -.->|Secrets Store<br/>CSI Driver<br/>Volume Mount| AUTH
    KV -.->|Secrets Store<br/>CSI Driver<br/>Volume Mount| GE
    KV -.->|Secrets Store<br/>CSI Driver<br/>Volume Mount| DA
    
    style CL fill:lightblue
    style ING fill:wheat
    style FE fill:lightgreen
    style GE fill:lightgreen
    style AUTH fill:lightgreen
    style DA fill:lightgreen
    style RF fill:pink
    style RG fill:pink
    style DB fill:pink
    style GOOGLE fill:yellow
    style KV fill:lavender
