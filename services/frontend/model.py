import os, requests
from bottle import HTTPError
from dotenv import load_dotenv

load_dotenv()

GAME_ENGINE_URL = os.environ["GAME_ENGINE_URL"]
AUTH_LOCAL = os.environ["AUTH_LOCAL"]
DATA_URL = os.environ["DATA_URL"]

def game_engine_init_user(uporabnik: str, mail: str, is_subscriber: str, timeout: float = 5.0) -> dict:
    """
    Tell the game engine who logged in. Raises HTTPError(502) on failure.
    Returns JSON payload if available, else {"ok": True}.
    """
    try:
        r = requests.post(
            f"{GAME_ENGINE_URL.rstrip('/')}/game/init_user",
            json={"uporabnik": uporabnik, "mail": mail, "is_subscriber": bool(is_subscriber)},
            timeout=timeout,
        )
        r.raise_for_status()
        if r.headers.get("content-type", "").startswith("application/json"):
            return r.json()
        return {"ok": True}
    except requests.RequestException as e:
        raise HTTPError(502, f"Game engine unavailable: {e}")


def frontend_redeem_ticket(ticket: str):
    r = requests.post(
        f"{AUTH_LOCAL.rstrip('/')}/auth/redeem",
        json={"ticket": ticket},
        timeout=(3, 10),
    )
    r.raise_for_status()
    return r.json()

def game_engine_ksp_move(id_igre: int, orozje: int, is_subscriber: bool, timeout: float = 5.0):
    """POST /game/ksp/poteza to the game engine and return JSON (if any)."""
    try:
        r = requests.post(
            f"{GAME_ENGINE_URL.rstrip('/')}/game/ksp/poteza",
            json={
                "id_igre": id_igre,
                "orozje": orozje,
                "is_subscriber": bool(is_subscriber),
            },
            timeout=timeout,
        )
    except requests.RequestException as e:
        raise HTTPError(502, f"Game engine unavailable: {e}")

    if r.status_code != 200:
        raise HTTPError(502, f"Game engine error: {r.status_code} {r.text}")

    return r.json() if r.headers.get("content-type","").startswith("application/json") else {"ok": True}

def game_engine_ksp_new_game(timeout: float = 10.0):
    """POST to /game/ksp/nova and return JSON (if any)."""
    try:
        r = requests.post(f"{GAME_ENGINE_URL.rstrip('/')}/game/ksp/nova", timeout=timeout)
        r.raise_for_status()
        return r.json() if r.headers.get("content-type","").startswith("application/json") else {"ok": True}
    except requests.HTTPError as e:
        raise HTTPError(r.status_code if 'r' in locals() else 502, f"Game engine error: {getattr(e.response, 'text', str(e))}")
    except requests.RequestException as e:
        raise HTTPError(502, f"Game engine unavailable: {e}")


def game_engine_get_ksp_state(id_igre: int, is_subscriber: bool, timeout: float = 10.0):
    """GET /game/ksp/state from the game engine. Returns JSON (if any) or text."""
    try:
        r = requests.get(
            f"{GAME_ENGINE_URL.rstrip('/')}/game/ksp/state",
            params={
                "id_igre": id_igre,
                "is_subscriber": "1" if is_subscriber else "0",
            },
            timeout=timeout,
        )
        r.raise_for_status()
    except requests.RequestException as e:
        raise HTTPError(502, f"Game engine unavailable: {e}")

    ctype = r.headers.get("content-type", "")
    return r.json() if ctype.startswith("application/json") else r.text

def data_ksp_history(mail: str, timeout=(2, 6)) -> list:
    """Return user's KSP history as a list; [] on error."""
    try:
        r = requests.get(
            f"{DATA_URL.rstrip('/')}/data/ksp/history",
            params={"username": mail},
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, list) else []
    except requests.RequestException as e:
        print(f"[history] fetch failed: {e}", flush=True)
        return []

def data_delete_ksp(username: str, timeout=(3, 10)):
    """POST to Data MS to delete a user's KSP rows. Returns JSON or {'ok': True}."""
    try:
        r = requests.post(
            f"{DATA_URL.rstrip('/')}/data/ksp/delete",
            json={"username": username},
            timeout=timeout,
        )
        r.raise_for_status()
        if r.headers.get("content-type", "").startswith("application/json"):
            return r.json()
        return {"ok": True}
    except requests.RequestException as e:
        raise HTTPError(502, f"Data service unavailable: {e}")

#====================================================================================================================

def game_engine_kspov_move(id_igre: int, orozje: int, is_subscriber: bool, timeout: float = 5.0):
    """POST /game/kspov/poteza to the game engine and return JSON (if any)."""
    try:
        r = requests.post(
            f"{GAME_ENGINE_URL.rstrip('/')}/game/kspov/poteza",
            json={
                "id_igre": int(id_igre),
                "orozje": orozje,
                "is_subscriber": bool(is_subscriber),
            },
            timeout=timeout,
        )
        r.raise_for_status()
    except requests.RequestException as e:
        raise HTTPError(502, f"Game engine unavailable: {e}")

    return r.json() if r.headers.get("content-type","").startswith("application/json") else {"ok": True}

def game_engine_kspov_new_game(timeout: float = 10.0):
    """POST /game/kspov/nova and return JSON (if any)."""
    try:
        r = requests.post(f"{GAME_ENGINE_URL.rstrip('/')}/game/kspov/nova", timeout=timeout)
        r.raise_for_status()
        return r.json() if r.headers.get("content-type", "").startswith("application/json") else {"ok": True}
    except requests.RequestException as e:
        raise HTTPError(502, f"Game engine unavailable: {e}")

def game_engine_get_kspov_state(id_igre: int, is_subscriber: bool, timeout: float = 10.0):
    """GET /game/kspov/state from the game engine. Returns JSON (if any) or text."""
    try:
        r = requests.get(
            f"{GAME_ENGINE_URL.rstrip('/')}/game/kspov/state",
            params={
                "id_igre": int(id_igre),
                "is_subscriber": "1" if is_subscriber else "0",
            },
            timeout=timeout,
        )
        r.raise_for_status()
    except requests.RequestException as e:
        raise HTTPError(502, f"Game engine unavailable: {e}")

    ctype = r.headers.get("content-type", "")
    return r.json() if ctype.startswith("application/json") else r.text


def data_kspov_history(mail: str, timeout=(2, 6)) -> list:
    """Return user's KŠPOV history as a list; [] on error."""
    try:
        r = requests.get(
            f"{DATA_URL.rstrip('/')}/data/kspov/history",
            params={"username": mail},
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, list) else []
    except requests.RequestException as e:
        print(f"[kspov history] fetch failed: {e}", flush=True)
        return []

def data_delete_kspov(username: str, timeout=(3, 10)):
    """POST /data/kspov/delete and return JSON (or {'ok': True})."""
    try:
        r = requests.post(
            f"{DATA_URL.rstrip('/')}/data/kspov/delete",
            json={"username": username},
            timeout=timeout,
        )
        r.raise_for_status()
        return r.json() if r.headers.get("content-type","").startswith("application/json") else {"ok": True}
    except requests.RequestException as e:
        raise HTTPError(502, f"Data service unavailable: {e}")
