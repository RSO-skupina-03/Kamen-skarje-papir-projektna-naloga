
OPENAPI_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "KSP Data Service API",
        "version": "1.0.2",
        "description": "Data microservice for persistent game history (PostgreSQL/Neon).",
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

        # ---------------- KSP ----------------
        "/data/ksp/insert": {
            "post": {
                "summary": "Insert KSP game result",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["username", "game_id", "player", "computer"],
                                "properties": {
                                    "username": {"type": "string"},
                                    "game_id": {"type": "integer"},
                                    "player": {"type": "integer"},
                                    "computer": {"type": "integer"},
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "200": {"description": "Inserted/updated"},
                    "400": {"description": "Missing field"},
                    "500": {"description": "Server error"},
                },
            }
        },
        "/data/ksp/get/id": {
            "get": {
                "summary": "Get next KSP game id",
                "parameters": [
                    {
                        "name": "username",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {
                    "200": {"description": "Returns game_id"},
                    "400": {"description": "Missing username"},
                    "500": {"description": "Server error"},
                },
            }
        },
        "/data/ksp/history": {
            "get": {
                "summary": "Get KSP history for user",
                "parameters": [
                    {
                        "name": "username",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {
                    "200": {"description": "History list"},
                    "400": {"description": "Missing username"},
                },
            }
        },
        "/data/ksp/delete": {
            "post": {
                "summary": "Delete KSP history for user",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["username"],
                                "properties": {"username": {"type": "string"}},
                            }
                        }
                    },
                },
                "responses": {
                    "200": {"description": "Deleted"},
                    "400": {"description": "Missing username"},
                    "500": {"description": "Server error"},
                },
            }
        },

        # ---------------- KSPOV ----------------
        "/data/kspov/insert": {
            "post": {
                "summary": "Insert KSPOV game result",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["username", "game_id", "player", "computer"],
                                "properties": {
                                    "username": {"type": "string"},
                                    "game_id": {"type": "integer"},
                                    "player": {"type": "integer"},
                                    "computer": {"type": "integer"},
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "200": {"description": "Inserted/updated"},
                    "400": {"description": "Missing field"},
                    "500": {"description": "Server error"},
                },
            }
        },
        "/data/kspov/get/id": {
            "get": {
                "summary": "Get next KSPOV game id",
                "parameters": [
                    {
                        "name": "username",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {
                    "200": {"description": "Returns game_id"},
                    "400": {"description": "Missing username"},
                    "500": {"description": "Server error"},
                },
            }
        },
        "/data/kspov/history": {
            "get": {
                "summary": "Get KSPOV history for user",
                "parameters": [
                    {
                        "name": "username",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {
                    "200": {"description": "History list"},
                    "400": {"description": "Missing username"},
                },
            }
        },
        "/data/kspov/delete": {
            "post": {
                "summary": "Delete KSPOV history for user",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["username"],
                                "properties": {"username": {"type": "string"}},
                            }
                        }
                    },
                },
                "responses": {
                    "200": {"description": "Deleted"},
                    "400": {"description": "Missing username"},
                    "500": {"description": "Server error"},
                },
            }
        },
    },
}

OPENAPI_SPEC["tags"] = [
    {"name": "Health", "description": "Liveness and readiness probes"},
    {"name": "KSP", "description": "Rock–Paper–Scissors data endpoints"},
    {"name": "KSPOV", "description": "Rock–Paper–Scissors–Fire–Water data endpoints"},
]

OPENAPI_SPEC["paths"]["/health"]["get"]["tags"] = ["Health"]
OPENAPI_SPEC["paths"]["/ready"]["get"]["tags"] = ["Health"]

OPENAPI_SPEC["paths"]["/data/ksp/insert"]["post"]["tags"] = ["KSP"]
OPENAPI_SPEC["paths"]["/data/ksp/get/id"]["get"]["tags"] = ["KSP"]
OPENAPI_SPEC["paths"]["/data/ksp/history"]["get"]["tags"] = ["KSP"]
OPENAPI_SPEC["paths"]["/data/ksp/delete"]["post"]["tags"] = ["KSP"]

OPENAPI_SPEC["paths"]["/data/kspov/insert"]["post"]["tags"] = ["KSPOV"]
OPENAPI_SPEC["paths"]["/data/kspov/get/id"]["get"]["tags"] = ["KSPOV"]
OPENAPI_SPEC["paths"]["/data/kspov/history"]["get"]["tags"] = ["KSPOV"]
OPENAPI_SPEC["paths"]["/data/kspov/delete"]["post"]["tags"] = ["KSPOV"]