import os, json, bottle, threading, model, redis
from bottle import request, response
from dotenv import load_dotenv

load_dotenv()

ksp = model.KSP()
kspov = model.KSPOV()

@bottle.route('/health', method=['GET', 'HEAD'])
def health_check():
    """Liveness probe - checks if the application is alive"""
    if request.method == 'HEAD':
        response.status = 200
        return
    response.content_type = 'application/json'
    return json.dumps({"status": "healthy", "service": "ksp-game-engine"})

@bottle.route('/ready', method=['GET', 'HEAD'])
def readiness_check():
    """Readiness probe - checks if the application is ready to serve traffic"""
    if request.method == 'HEAD':
        response.status = 200
        return

    checks = {
        "status": "ready",
        "service": "ksp-game-engine",
        "checks": {}
    }

    try:
        db_url = os.environ.get("DB_URL")
        redis_host = os.environ.get("REDIS_HOST")
        redis_port = os.environ.get("REDIS_PORT")
        redis_db = os.environ.get("REDIS_DB")

        checks["checks"]["environment"] = {
            "DB_URL": "ok" if db_url else "missing",
            "REDIS_HOST": "ok" if redis_host else "missing",
            "REDIS_PORT": "ok" if redis_port else "missing",
            "REDIS_DB": "ok" if redis_db else "missing"
        }

        # Redis ping check
        redis_check = {"status": "skipped"}
        if redis_host and redis_port and redis_db is not None:
            try:
                rds = redis.Redis(
                    host=redis_host,
                    port=int(redis_port),
                    db=int(redis_db),
                    socket_connect_timeout=1,
                    socket_timeout=1,
                    decode_responses=True,
                )
                pong = rds.ping()
                redis_check = {"status": "ok" if pong else "fail"}
            except Exception as e:
                redis_check = {"status": "fail", "error": str(e)}

        checks["checks"]["redis"] = redis_check

        # Determine overall readiness (env vars + redis must be ok)
        all_ok = (
            db_url and
            redis_host and
            redis_port and
            (redis_db is not None) and
            checks["checks"]["redis"]["status"] == "ok"
        )

        if all_ok:
            response.status = 200
            checks["status"] = "ready"
        else:
            response.status = 503
            checks["status"] = "not ready"

    except Exception as e:
        response.status = 503
        checks["status"] = "error"
        checks["error"] = str(e)

    response.content_type = 'application/json'
    return json.dumps(checks, indent=2)

@bottle.post("/game/init_user")
def init_user():
    data = request.json or {}

    user = data.get("uporabnik")
    is_subscriber = bool(data.get("is_subscriber"))
    mail = data.get("mail")

    # Nastavi uporabnika v modelih
    ksp.nastavi_uporabnika(mail)
    kspov.nastavi_uporabnika(mail)

    # To nastavi ko bos sel delat zgodovino
    if is_subscriber:
        kspov.get_id_kspov()
        ksp.get_id_ksp()
    else:
        ksp.nastavi_id(ksp.prosti_id_igre())
        kspov.nastavi_id(kspov.prosti_id_igre())
    # po želji vrneš ID-je, če jih frontend kdaj rabi
    payload = {
        "status": "ok",
        "user": user,
    }

    response.content_type = "application/json"
    return json.dumps(payload)

#================================================================================================================================================

def compute_ksp_state(id_igre: int, is_subscriber: bool):
    if id_igre not in ksp.igre:
        return {"action": "new_game"}

    igra = ksp.igre[id_igre]
    finished = igra.zmaga_igralca() or igra.zmaga_racunalnika()

    if finished:
        # To nastavi ko bos sel delat zgoodvino
        if is_subscriber:
            # ksp.insert_game_ksp(id_igre, igra.koncni_izid_igralca(), igra.koncni_izid_racunalnika())
            threading.Thread(
                 target=ksp.insert_game_ksp,
                 args=(id_igre, igra.koncni_izid_igralca(), igra.koncni_izid_racunalnika()),
                 daemon=False,
             ).start()
        else:
            ksp.igre.pop(id_igre, None)
            ksp.shrani_v_datoteko()
            ksp.nastavi_id(ksp.prosti_id_igre())

    return {
        "action": "ok",
        "id_igre": id_igre,
        "is_subscriber": is_subscriber,
        "finished": finished,
        "igra": {
            "delni_izid_igralca": igra.delni_izid_igralca(),
            "delni_izid_racunalnika": igra.delni_izid_racunalnika(),
            "koncni_izid_igralca": igra.koncni_izid_igralca(),
            "koncni_izid_racunalnika": igra.koncni_izid_racunalnika(),
            "zmaga_igralca": igra.zmaga_igralca(),
            "zmaga_racunalnika": igra.zmaga_racunalnika(),
        },
    }

@bottle.post("/game/ksp/nova")
def ksp_new():
    """Ustvari novo igro in vrni njen ID kot JSON."""
    id_nova_igra = ksp.nova_igra()

    response.content_type = "application/json"
    return json.dumps({"id_igre": id_nova_igra})

@bottle.route("/game/ksp/state", method=["GET"])
def api_ksp_state():
    try:
        id_igre = int(request.query.get("id_igre"))
    except (TypeError, ValueError):
        response.status = 400
        return {"error": "id_igre parameter is required and must be int"}

    is_subscriber = request.query.get("is_subscriber") == "1"

    result = compute_ksp_state(id_igre, is_subscriber)

    response.content_type = "application/json"
    return json.dumps(result)

@bottle.post("/game/ksp/poteza")
def ksp_move_api():
    data = request.json or {}
    try:
        id_igre = int(data.get("id_igre"))
        orozje = int(data.get("orozje"))
    except (TypeError, ValueError):
        response.status = 400
        return {"error": "id_igre and orozje must be integers"}

    # 1) izvede potezo na modelu
    ksp.potek_igre(id_igre, orozje)

    # 2) vrne morda samo OK (frontend bo itak še enkrat klical /game/ksp/state)
    response.content_type = "application/json"
    return json.dumps({"status": "ok"})
#====================================================================================================================================================

def compute_kspov_state(id_igre: int, is_subscriber: bool):
    if id_igre not in kspov.igre:
        return {"action": "new_game"}

    igra = kspov.igre[id_igre]
    finished = igra.zmaga_igralca_1() or igra.zmaga_racunalnika_1()

    if finished:
        if is_subscriber:
            #kspov.insert_game_kspov(id_igre, igra.koncni_izid_igralca_1(), igra.koncni_izid_racunalnika_1())
            threading.Thread(
                target=kspov.insert_game_kspov,
                args=(id_igre, igra.koncni_izid_igralca_1(), igra.koncni_izid_racunalnika_1()),
                daemon=False,
            ).start()
        else:
            kspov.igre.pop(id_igre, None)
            kspov.shrani_v_datoteko()
            kspov.nastavi_id(len(kspov.igre))

    return {
        "action": "ok",
        "id_igre": id_igre,
        "is_subscriber": is_subscriber,
        "finished": finished,
        "igra": {
            "delni_izid_igralca": igra.delni_izid_igralca(),
            "delni_izid_racunalnika": igra.delni_izid_racunalnika(),
            "koncni_izid_igralca": igra.koncni_izid_igralca_1(),
            "koncni_izid_racunalnika": igra.koncni_izid_racunalnika_1(),
            "zmaga_igralca": igra.zmaga_igralca_1(),
            "zmaga_racunalnika": igra.zmaga_racunalnika_1(),
        },
    }

@bottle.post("/game/kspov/nova")
def kspov_new():
    """Ustvari novo igro in vrni njen ID kot JSON."""
    id_nova_igra = kspov.nova_igra_1()

    response.content_type = "application/json"
    return json.dumps({"id_igre": id_nova_igra})

@bottle.route("/game/kspov/state", method=["GET"])
def api_kspov_state():
    try:
        id_igre = int(request.query.get("id_igre"))
    except (TypeError, ValueError):
        response.status = 400
        return {"error": "id_igre parameter is required and must be int"}

    is_subscriber = request.query.get("is_subscriber") == "1"

    result = compute_kspov_state(id_igre, is_subscriber)

    response.content_type = "application/json"
    return json.dumps(result)

@bottle.post("/game/kspov/poteza")
def kspov_move_api():
    data = request.json or {}
    try:
        id_igre = int(data.get("id_igre"))
        orozje = int(data.get("orozje"))
    except (TypeError, ValueError):
        response.status = 400
        return {"error": "id_igre and orozje must be integers"}
    
    # 1) izvede potezo na modelu
    kspov.potek_igre_1(id_igre, orozje)

    # 2) vrne morda samo OK (frontend bo itak še enkrat klical /game/kspov/state)
    response.content_type = "application/json"
    return json.dumps({"status": "ok"})

app = bottle.default_app()

if __name__ == "__main__":
    bottle.run(app=app, host="localhost", port=8081, debug=True)