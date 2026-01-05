OPENAPI_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "KSP Game Engine Service API",
        "version": "1.0.2",
        "description": "Game engine microservice (KSP + KSPOV). Stores game state in Redis and writes history via Data Service.",
    },
    "paths": {
        "/health": {
            "get": {
                "summary": "Liveness probe",
                "responses": {"200": {"description": "Service is alive"}}
            }
        },
        "/ready": {
            "get": {
                "summary": "Readiness probe",
                "responses": {
                    "200": {"description": "Service is ready"},
                    "503": {"description": "Service is not ready"},
                }
            }
        },
        "/game/init_user": {
            "post": {
                "summary": "Initialize user context",
                "description": "Sets user in KSP/KSPoV models and initializes IDs depending on subscriber status.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "uporabnik": {"type": "string"},
                                    "mail": {"type": "string"},
                                    "is_subscriber": {"type": "boolean"},
                                },
                                "required": ["mail"],
                            }
                        }
                    },
                },
                "responses": {
                    "200": {"description": "Initialized"},
                    "400": {"description": "Bad request"},
                    "500": {"description": "Server error"},
                },
            }
        },

        # ---------------- KSP ----------------
        "/game/ksp/nova": {
            "post": {
                "summary": "Create a new KSP game",
                "responses": {
                    "200": {
                        "description": "Returns new game id",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"id_igre": {"type": "integer"}},
                                }
                            }
                        },
                    }
                },
            }
        },
        "/game/ksp/state": {
            "get": {
                "summary": "Get KSP game state",
                "parameters": [
                    {"name": "id_igre", "in": "query", "required": True, "schema": {"type": "integer"}},
                    {
                        "name": "is_subscriber",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "string", "enum": ["0", "1"]},
                        "description": "Set to '1' if subscriber.",
                    },
                ],
                "responses": {
                    "200": {"description": "State response"},
                    "400": {"description": "Invalid parameters"},
                },
            }
        },
        "/game/ksp/poteza": {
            "post": {
                "summary": "Play a move (KSP)",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["id_igre", "orozje"],
                                "properties": {
                                    "id_igre": {"type": "integer"},
                                    "orozje": {"type": "integer", "description": "Player move code"},
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "200": {"description": "OK"},
                    "400": {"description": "Invalid parameters"},
                },
            }
        },

        # ---------------- KSPOV ----------------
        "/game/kspov/nova": {
            "post": {
                "summary": "Create a new KSPOV game",
                "responses": {
                    "200": {
                        "description": "Returns new game id",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"id_igre": {"type": "integer"}},
                                }
                            }
                        },
                    }
                },
            }
        },
        "/game/kspov/state": {
            "get": {
                "summary": "Get KSPOV game state",
                "parameters": [
                    {"name": "id_igre", "in": "query", "required": True, "schema": {"type": "integer"}},
                    {
                        "name": "is_subscriber",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "string", "enum": ["0", "1"]},
                        "description": "Set to '1' if subscriber.",
                    },
                ],
                "responses": {
                    "200": {"description": "State response"},
                    "400": {"description": "Invalid parameters"},
                },
            }
        },
        "/game/kspov/poteza": {
            "post": {
                "summary": "Play a move (KSPOV)",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["id_igre", "orozje"],
                                "properties": {
                                    "id_igre": {"type": "integer"},
                                    "orozje": {"type": "integer", "description": "Player move code"},
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "200": {"description": "OK"},
                    "400": {"description": "Invalid parameters"},
                },
            }
        },
    },
}

# ---- Tag definitions (optional but recommended; gives nice descriptions in Swagger UI) ----
OPENAPI_SPEC["tags"] = [
    {"name": "Health", "description": "Liveness and readiness probes"},
    {"name": "Users", "description": "User/session initialization for the game engine"},
    {"name": "KSP", "description": "Rock–Paper–Scissors game endpoints"},
    {"name": "KSPOV", "description": "Rock–Paper–Scissors–Fire–Water game endpoints"},
]

# ---- Assign tags to operations (removes the 'default' group) ----
OPENAPI_SPEC["paths"]["/health"]["get"]["tags"] = ["Health"]
OPENAPI_SPEC["paths"]["/ready"]["get"]["tags"] = ["Health"]

OPENAPI_SPEC["paths"]["/game/init_user"]["post"]["tags"] = ["Users"]

OPENAPI_SPEC["paths"]["/game/ksp/nova"]["post"]["tags"] = ["KSP"]
OPENAPI_SPEC["paths"]["/game/ksp/state"]["get"]["tags"] = ["KSP"]
OPENAPI_SPEC["paths"]["/game/ksp/poteza"]["post"]["tags"] = ["KSP"]

OPENAPI_SPEC["paths"]["/game/kspov/nova"]["post"]["tags"] = ["KSPOV"]
OPENAPI_SPEC["paths"]["/game/kspov/state"]["get"]["tags"] = ["KSPOV"]
OPENAPI_SPEC["paths"]["/game/kspov/poteza"]["post"]["tags"] = ["KSPOV"]