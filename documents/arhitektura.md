---
config:
  layout: elk
---
flowchart TB
    CL["Client"] -- HTTP --> FE["Frontend & Session & API Gateway Service"]
    FE -- HTTP --> GE["Game Engine Service"] & AUTH["Authentication Service"]
    AUTH -- OAuth2/OIDC --> GOOGLE[("Google Auth Platform")]
    GE -- Redis HSET/HGET --> R[("Redis")]
    GE -- HTTP --> DA["Data Service"]
    DA -- SQL insert/get/delete --> DB[("Neon Database (PostgreSQL)")]
    FE -- HTTP --> DA