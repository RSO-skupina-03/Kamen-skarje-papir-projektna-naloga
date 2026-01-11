OPENAPI_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "KSP Frontend & API Gateway Service API",
        "version": "1.0.2",
        "description": "Frontend UI + session cookies + gateway endpoints.",
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
        "/env.js": {
            "get": {
                "summary": "Runtime config for browser",
                "description": "Returns window.__ENV__ with frontend configuration.",
                "responses": {
                    "200": {"description": "JavaScript config"},
                }
            }
        },
        "/metrics": {
            "get": {
                "summary": "Gateway metrics",
                "responses": {
                    "200": {"description": "Metrics JSON"},
                }
            }
        },
        "/gateway/health": {
            "get": {
                "summary": "Gateway + backend health check",
                "description": "Checks health of downstream services (game_engine/auth/data).",
                "responses": {
                    "200": {"description": "Health summary"},
                }
            }
        },
        "/": {
            "get": {
                "summary": "Login page",
                "responses": {"200": {"description": "HTML login page"}}
            },
            "head": {
                "summary": "Login page (HEAD)",
                "responses": {"200": {"description": "OK"}}
            }
        },
        "/frontend/login": {
            "options": {
                "summary": "CORS preflight for login",
                "responses": {"200": {"description": "OK"}}
            },
            "put": {
                "summary": "Login as Guest/User",
                "description": "Sets session cookies and initializes user in game_engine.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {"uporabnik": {"type": "string"}},
                            }
                        }
                    }
                },
                "responses": {
                    "303": {"description": "Redirect to /igra"},
                    "200": {"description": "OK"},
                }
            },
            "head": {
                "summary": "Login (HEAD) — redirect",
                "responses": {"303": {"description": "Redirect to /igra"}}
            }
        },
        "/auth/finalize": {
            "get": {
                "summary": "Finalize Google login",
                "description": "Redeems one-time ticket at auth service, sets cookies, initializes user in game_engine, redirects to /igra.",
                "parameters": [
                    {"name": "ticket", "in": "query", "required": True, "schema": {"type": "string"}},
                ],
                "responses": {
                    "303": {"description": "Redirect to /igra"},
                    "400": {"description": "Missing ticket"},
                }
            }
        },
        "/igra": {
            "get": {
                "summary": "Game menu page",
                "description": "Requires 'uporabnik' cookie; otherwise redirects to '/'.",
                "responses": {
                    "200": {"description": "HTML game menu"},
                    "303": {"description": "Redirect to /"},
                }
            },
            "head": {
                "summary": "Game menu (HEAD)",
                "responses": {"200": {"description": "OK"}}
            }
        },
        "/ksp": {
            "get": {
                "summary": "KSP game page",
                "description": "Renders the KSP game page. Requires game id cookie; redirects to /nova_igra_ksp if missing.",
                "responses": {
                    "200": {"description": "HTML KSP page"},
                    "303": {"description": "Redirect to /nova_igra_ksp or /ksp"},
                },
            },
            "head": {
                "summary": "KSP game page (HEAD)",
                "responses": {"200": {"description": "OK"}},
            },
            "post": {
                "summary": "Submit KSP move",
                "description": "Reads game id from cookie and 'orozje' from form, sends move to game_engine, then redirects back to /ksp.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "orozje": {"type": "integer", "description": "Player choice (kamen/škarje/papir) code"},
                                },
                                "required": ["orozje"],
                            }
                        }
                    },
                },
                "responses": {
                    "303": {"description": "Redirect to /ksp (or /nova_igra_ksp)"},
                    "200": {"description": "OK"},
                },
            },
        },

        "/nova_igra_ksp": {
            "get": {
                "summary": "Create new KSP game (frontend)",
                "description": "Calls game_engine to create a new KSP game, stores id in cookie, redirects to /ksp.",
                "responses": {
                    "303": {"description": "Redirect to /ksp"},
                    "200": {"description": "OK"},
                },
            },
            "head": {
                "summary": "Create new KSP game (HEAD)",
                "responses": {
                    "303": {"description": "Redirect"},
                },
            },
        },

        "/zgodovina_ksp": {
            "get": {
                "summary": "Show KSP history page",
                "description": "Renders history page for the logged-in user; calls Data Service for history.",
                "responses": {
                    "200": {"description": "HTML history page"},
                    "303": {"description": "Redirect to / (if not logged in)"},
                },
            },
            "head": {
                "summary": "Show KSP history page (HEAD)",
                "responses": {"200": {"description": "OK"}},
            },
        },

        "/brisi_ksp": {
            "delete": {
                "summary": "Delete KSP history",
                "description": "Deletes user's KSP history via Data Service, then redirects to /zgodovina_ksp.",
                "responses": {
                    "303": {"description": "Redirect to /zgodovina_ksp"},
                    "401": {"description": "Not logged in"},
                    "200": {"description": "OK"},
                },
            },
            "head": {
                "summary": "Delete KSP history (HEAD)",
                "responses": {"200": {"description": "OK"}},
            },
        },
        "/kspov": {
            "get": {
                "summary": "KSPOV game page",
                "description": "Renders the KSPOV game page. Requires game id cookie; redirects to /nova_igra_kspov if missing.",
                "responses": {
                    "200": {"description": "HTML KSPOV page"},
                    "303": {"description": "Redirect to /nova_igra_kspov or /kspov"},
                },
            },
            "head": {
                "summary": "KSPOV game page (HEAD)",
                "responses": {"200": {"description": "OK"}},
            },
            "post": {
                "summary": "Submit KSPOV move",
                "description": "Reads game id from cookie and 'orozje' from form, sends move to game_engine, then redirects back to /kspov.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "orozje": {"type": "integer", "description": "Player choice code (kamen/škarje/papir/ogenj/voda)"},
                                },
                                "required": ["orozje"],
                            }
                        }
                    },
                },
                "responses": {
                    "303": {"description": "Redirect to /kspov (or /nova_igra_kspov)"},
                    "200": {"description": "OK"},
                },
            },
        },
    
        "/nova_igra_kspov": {
            "get": {
                "summary": "Create new KSPOV game (frontend)",
                "description": "Calls game_engine to create a new KSPOV game, stores id in cookie, redirects to /kspov.",
                "responses": {
                    "303": {"description": "Redirect to /kspov"},
                    "200": {"description": "OK"},
                },
            },
            "head": {
                "summary": "Create new KSPOV game (HEAD)",
                "responses": {
                    "303": {"description": "Redirect"},
                },
            },
        },
    
        "/zgodovina_kspov": {
            "get": {
                "summary": "Show KSPOV history page",
                "description": "Renders history page for the logged-in user; calls Data Service for history.",
                "responses": {
                    "200": {"description": "HTML history page"},
                    "303": {"description": "Redirect to / (if not logged in)"},
                },
            },
            "head": {
                "summary": "Show KSPOV history page (HEAD)",
                "responses": {"200": {"description": "OK"}},
            },
        },
    
        "/brisi_kspov": {
            "delete": {
                "summary": "Delete KSPOV history",
                "description": "Deletes user's KSPOV history via Data Service, then redirects to /zgodovina_kspov.",
                "responses": {
                    "303": {"description": "Redirect to /zgodovina_kspov"},
                    "401": {"description": "Not logged in"},
                    "200": {"description": "OK"},
                },
            },
            "head": {
                "summary": "Delete KSPOV history (HEAD)",
                "responses": {"200": {"description": "OK"}},
            },
        },
        "/docs/frontend": {
            "get": {
                "summary": "Swagger UI — Frontend API",
                "description": "Serves Swagger UI for the Frontend & API Gateway service. UI loads this service's OpenAPI JSON (typically /docs.json).",
                "responses": {
                    "200": {"description": "HTML Swagger UI page"}
                },
            }
        },
        "/docs/game-engine": {
            "get": {
                "summary": "Swagger UI — Game Engine API",
                "description": "Serves Swagger UI for the Game Engine service via the Frontend. The UI should load a proxied OpenAPI JSON (e.g., /docs/game-engine.json).",
                "responses": {
                    "200": {"description": "HTML Swagger UI page"}
                },
            }
        },
        "/docs/data": {
            "get": {
                "summary": "Swagger UI — Data Service API",
                "description": "Serves Swagger UI for the Data service via the Frontend. The UI should load a proxied OpenAPI JSON (e.g., /docs/data.json).",
                "responses": {
                    "200": {"description": "HTML Swagger UI page"}
                },
            }
        },
        "/docs/auth": {
            "get": {
                "summary": "Swagger UI — Authentication Service API",
                "description": "Serves Swagger UI for the Auth service via the Frontend. The UI should load a proxied OpenAPI JSON (e.g., /docs/auth.json).",
                "responses": {
                    "200": {"description": "HTML Swagger UI page"}
                },
            }
        },
    },
}

# ---- Tag definitions (optional but recommended; gives nice descriptions in Swagger UI) ----
OPENAPI_SPEC["tags"] = [
    {"name": "Health", "description": "Liveness and readiness probes"},
    {"name": "Gateway", "description": "Gateway diagnostics (backend health, metrics)"},
    {"name": "Frontend", "description": "UI pages and runtime config"},
    {"name": "Auth", "description": "Authentication finalize flow (ticket redemption)"},
    {"name": "KSP", "description": "Rock–Paper–Scissors game endpoints"},
    {"name": "KSPOV", "description": "Rock–Paper–Scissors–Fire–Water game endpoints"},
    {"name": "Docs", "description": "Swagger UI pages (documentation portals)"}
]

# ---- Assign tags to operations (removes the 'default' group) ----
OPENAPI_SPEC["paths"]["/health"]["get"]["tags"] = ["Health"]
OPENAPI_SPEC["paths"]["/ready"]["get"]["tags"] = ["Health"]

OPENAPI_SPEC["paths"]["/gateway/health"]["get"]["tags"] = ["Gateway"]
OPENAPI_SPEC["paths"]["/metrics"]["get"]["tags"] = ["Gateway"]

OPENAPI_SPEC["paths"]["/env.js"]["get"]["tags"] = ["Frontend"]
OPENAPI_SPEC["paths"]["/"]["get"]["tags"] = ["Frontend"]
OPENAPI_SPEC["paths"]["/"]["head"]["tags"] = ["Frontend"]
OPENAPI_SPEC["paths"]["/igra"]["get"]["tags"] = ["Frontend"]
OPENAPI_SPEC["paths"]["/igra"]["head"]["tags"] = ["Frontend"]

OPENAPI_SPEC["paths"]["/frontend/login"]["options"]["tags"] = ["Frontend"]
OPENAPI_SPEC["paths"]["/frontend/login"]["put"]["tags"] = ["Frontend"]
OPENAPI_SPEC["paths"]["/frontend/login"]["head"]["tags"] = ["Frontend"]
OPENAPI_SPEC["paths"]["/ksp"]["get"]["tags"] = ["Frontend"]
OPENAPI_SPEC["paths"]["/ksp"]["head"]["tags"] = ["Frontend"]
OPENAPI_SPEC["paths"]["/kspov"]["get"]["tags"] = ["Frontend"]
OPENAPI_SPEC["paths"]["/kspov"]["head"]["tags"] = ["Frontend"]

OPENAPI_SPEC["paths"]["/auth/finalize"]["get"]["tags"] = ["Auth"]

OPENAPI_SPEC["paths"]["/ksp"]["post"]["tags"] = ["KSP"]
OPENAPI_SPEC["paths"]["/nova_igra_ksp"]["get"]["tags"] = ["KSP"]
OPENAPI_SPEC["paths"]["/nova_igra_ksp"]["head"]["tags"] = ["KSP"]
OPENAPI_SPEC["paths"]["/zgodovina_ksp"]["get"]["tags"] = ["KSP"]
OPENAPI_SPEC["paths"]["/zgodovina_ksp"]["head"]["tags"] = ["KSP"]
OPENAPI_SPEC["paths"]["/brisi_ksp"]["delete"]["tags"] = ["KSP"]
OPENAPI_SPEC["paths"]["/brisi_ksp"]["head"]["tags"] = ["KSP"]

OPENAPI_SPEC["paths"]["/kspov"]["post"]["tags"] = ["KSPOV"]

OPENAPI_SPEC["paths"]["/nova_igra_kspov"]["get"]["tags"] = ["KSPOV"]
OPENAPI_SPEC["paths"]["/nova_igra_kspov"]["head"]["tags"] = ["KSPOV"]
OPENAPI_SPEC["paths"]["/zgodovina_kspov"]["get"]["tags"] = ["KSPOV"]
OPENAPI_SPEC["paths"]["/zgodovina_kspov"]["head"]["tags"] = ["KSPOV"]
OPENAPI_SPEC["paths"]["/brisi_kspov"]["delete"]["tags"] = ["KSPOV"]
OPENAPI_SPEC["paths"]["/brisi_kspov"]["head"]["tags"] = ["KSPOV"]

OPENAPI_SPEC["paths"]["/docs/frontend"]["get"]["tags"] = ["Docs"]
OPENAPI_SPEC["paths"]["/docs/game-engine"]["get"]["tags"] = ["Docs"]
OPENAPI_SPEC["paths"]["/docs/data"]["get"]["tags"] = ["Docs"]
OPENAPI_SPEC["paths"]["/docs/auth"]["get"]["tags"] = ["Docs"]