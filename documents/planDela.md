# Implementacija mikrostoritev

- API Gateway: 
Single entry point, routes requests to internal services, does simple aggregation.

- Auth/Session Service:  
Manages users, logins, and issues tokens/sessions that other services trust.

- Game Engine Service: 
Contains all core game rules and manages in-progress game sessions.

- History Service: 
Stores completed games and exposes them for statistics and user history views.