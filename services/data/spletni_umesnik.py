import os, json, bottle, model, swagger
from bottle import request, response, HTTPError
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.environ["DB_URL"]

@bottle.route('/health', method=['GET', 'HEAD'])
def health_check():
    """Liveness probe - checks if the application is alive"""
    if request.method == 'HEAD':
        response.status = 200
        return
    response.content_type = 'application/json'
    return json.dumps({"status": "healthy", "service": "ksp-data"})

@bottle.route('/ready', method=['GET', 'HEAD'])
def readiness_check():
    """Readiness probe - checks if the application is ready to serve traffic"""
    if request.method == 'HEAD':
        response.status = 200
        return
    
    # Check required environment variables
    checks = {
        "status": "ready",
        "service": "ksp-data",
        "checks": {}
    }
    
    # Check if required environment variables are set
    try:
        db_url = os.environ.get("DB_URL")
        
        checks["checks"]["environment"] = {
            "DB_URL": "ok" if db_url else "missing"
        }
        
        # Determine overall readiness
        all_ok = (
            db_url
        )
        
        if all_ok:
            response.status = 200
            checks["status"] = "ready"
        else:
            response.status = 503  # Service Unavailable
            checks["status"] = "not ready"
            
    except Exception as e:
        response.status = 503
        checks["status"] = "error"
        checks["error"] = str(e)
    
    response.content_type = 'application/json'
    return json.dumps(checks, indent=2)

@bottle.get("/docs.json")
def docs_json():
    response.content_type = "application/json; charset=utf-8"
    return json.dumps(swagger.OPENAPI_SPEC, ensure_ascii=False, indent=2)

@bottle.post("/data/ksp/insert")
def ksp_insert():
    data = request.json or {}
    # required fields only; no type validation
    try:
        username = data["username"]
        game_id  = data["game_id"]
        player   = data["player"]
        computer = data["computer"]
    except KeyError as e:
        raise HTTPError(400, f"Missing field: {e.args[0]}")

    affected = model.insert_game_ksp(username, game_id, player, computer)

    response.content_type = "application/json"
    return json.dumps({"ok": True, "affected": int(affected), "username": username, "game_id": game_id})

@bottle.get("/data/ksp/get/id")
def data_get_id():
    mail = (request.query.get("username"))
    if not mail:
        raise HTTPError(400, "Missing 'username' (or 'mail'/'email') query parameter")

    try:
        game_id = model.get_id_ksp(mail)
        response.content_type = "application/json; charset=utf-8"
        return json.dumps({"game_id": game_id}, ensure_ascii=False)
    except Exception as e:
        raise HTTPError(500, f"Failed to get game_id: {e}")

@bottle.get("/data/ksp/history")
def history_ksp():
    mail = request.query.get("username")
    if not mail:
        raise HTTPError(400, "Missing username/mail/email")
    data = model.get_user_history_ksp_list(mail)
    response.content_type = "application/json; charset=utf-8"
    return json.dumps(data, ensure_ascii=False)

@bottle.post("/data/ksp/delete")
def ksp_insert():
    username = request.json.get("username")
    if not username:
        raise HTTPError(400, "Missing field: username")

    try:
        affected = model.delete_ksp(username)  # should return int (rows deleted)
    except Exception as e:  # optionally catch DB-specific errors
        raise HTTPError(500, f"Delete failed: {e}")

    response.content_type = "application/json"
    return json.dumps({"ok": True, "affected": int(affected)}, ensure_ascii=False)

#===============================================================================================================

@bottle.post("/data/kspov/insert")
def kspov_insert():
    data = request.json or {}
    # required fields only; no type validation
    try:
        username = data["username"]
        game_id  = data["game_id"]
        player   = data["player"]
        computer = data["computer"]
    except KeyError as e:
        raise HTTPError(400, f"Missing field: {e.args[0]}")

    affected = model.insert_game_kspov(username, game_id, player, computer)

    response.content_type = "application/json"
    return json.dumps({"ok": True, "affected": int(affected), "username": username, "game_id": game_id})

@bottle.get("/data/kspov/get/id")
def data_get_id():
    mail = (request.query.get("username"))
    if not mail:
        raise HTTPError(400, "Missing 'username' (or 'mail'/'email') query parameter")

    try:
        game_id = model.get_id_kspov(mail)
        response.content_type = "application/json; charset=utf-8"
        return json.dumps({"game_id": game_id}, ensure_ascii=False)
    except Exception as e:
        raise HTTPError(500, f"Failed to get game_id: {e}")

@bottle.get("/data/kspov/history")
def history_kspov():
    mail = request.query.get("username")
    if not mail:
        raise HTTPError(400, "Missing username/mail/email")
    data = model.get_user_history_kspov_list(mail)
    response.content_type = "application/json; charset=utf-8"
    return json.dumps(data, ensure_ascii=False)

@bottle.post("/data/kspov/delete")
def kspov_insert():
    username = request.json.get("username")
    if not username:
        raise HTTPError(400, "Missing field: username")

    try:
        affected = model.delete_kspov(username)  # should return int (rows deleted)
    except Exception as e:  # optionally catch DB-specific errors
        raise HTTPError(500, f"Delete failed: {e}")

    response.content_type = "application/json"
    return json.dumps({"ok": True, "affected": int(affected)}, ensure_ascii=False)

app = bottle.default_app()

if __name__ == "__main__":
    bottle.run(app=app, host="localhost", port=8083, debug=True)