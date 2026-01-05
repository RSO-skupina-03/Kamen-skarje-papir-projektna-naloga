OPENAPI_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "KSP Authentication Service API",
        "version": "1.0.2",
        "description": "Authentication microservice (Google OAuth2/OIDC + one-time ticket redeem).",
    },
    "paths": {
        "/health": {
            "get": {
                "summary": "Liveness probe",
                "responses": {
                    "200": {
                        "description": "Service is alive",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"}
                            }
                        },
                    }
                },
            }
        },
        "/ready": {
            "get": {
                "summary": "Readiness probe",
                "responses": {
                    "200": {"description": "Service is ready"},
                    "503": {"description": "Service is not ready"},
                },
            }
        },
        "/auth/google/login": {
            "get": {
                "summary": "Start Google OAuth2/OIDC login",
                "description": "Redirects the browser to Google Authorization endpoint.",
                "parameters": [
                    {
                        "name": "redirect_to",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "string"},
                        "description": "Frontend URL to redirect to after successful login.",
                    }
                ],
                "responses": {
                    "302": {"description": "Redirect to Google login"},
                },
            }
        },
        "/auth/google/callback": {
            "get": {
                "summary": "Google OAuth callback",
                "description": "Handles Google callback, verifies ID token, generates one-time ticket, then redirects to frontend finalize endpoint.",
                "parameters": [
                    {"name": "code", "in": "query", "required": True, "schema": {"type": "string"}},
                    {"name": "state", "in": "query", "required": True, "schema": {"type": "string"}},
                ],
                "responses": {
                    "303": {"description": "Redirect to frontend /auth/finalize?ticket=..."},
                    "400": {"description": "Missing/invalid code/state"},
                    "401": {"description": "Invalid ID token"},
                },
            }
        },
        "/auth/redeem": {
            "post": {
                "summary": "Redeem one-time ticket",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {"ticket": {"type": "string"}},
                                "required": ["ticket"],
                            }
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Authenticated user payload",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "email": {"type": "string"},
                                        "sub": {"type": "string"},
                                        "iat": {"type": "integer"},
                                    },
                                }
                            }
                        },
                    },
                    "400": {"description": "Invalid or expired ticket"},
                },
            }
        },
    },
}

# ---- Tag definitions (optional but recommended; gives nice descriptions in Swagger UI) ----
OPENAPI_SPEC["tags"] = [
    {"name": "Health", "description": "Liveness and readiness probes"},
    {"name": "Google OAuth", "description": "Google OAuth2/OIDC login and callback flow"},
    {"name": "Tickets", "description": "One-time ticket redemption"},
]

# ---- Assign tags to operations (removes the 'default' group) ----
OPENAPI_SPEC["paths"]["/health"]["get"]["tags"] = ["Health"]
OPENAPI_SPEC["paths"]["/ready"]["get"]["tags"] = ["Health"]

OPENAPI_SPEC["paths"]["/auth/google/login"]["get"]["tags"] = ["Google OAuth"]
OPENAPI_SPEC["paths"]["/auth/google/callback"]["get"]["tags"] = ["Google OAuth"]

OPENAPI_SPEC["paths"]["/auth/redeem"]["post"]["tags"] = ["Tickets"]