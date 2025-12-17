import os, json, tempfile, threading, psycopg
from pathlib import Path
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool

load_dotenv()
DB_URL = os.environ["DB_URL"]
DATOTEKA_KSP = 'datoteke/ksp.json'
DATOTEKA_KSPOV = 'datoteke/kspov.json'

# Lazy, thread-safe pool init (avoids forking issues with dev reloaders)
_POOL = None
_POOL_LOCK = threading.Lock()

def get_pool() -> ConnectionPool:
    global _POOL
    if _POOL is None:
        with _POOL_LOCK:
            if _POOL is None:
                _POOL = ConnectionPool(
                    DB_URL,
                    min_size=1,
                    max_size=4,
                    max_idle=60,        # recycle idle conns
                    max_lifetime=600,   # recycle long-lived conns
                    timeout=5,
                    open=True           # silence deprecation, open now
                )
    return _POOL


def _exec_with_retry(sql, params=(), mode: str = "none"):
    """
    Execute a single SQL statement with a 1x retry on stale/broken connections.

    mode:
      - "none"     : execute, return None
      - "one"      : execute, return cursor.fetchone()
      - "all"      : execute, return cursor.fetchall()
      - "rowcount" : execute, return cursor.rowcount (int)
    """
    pool = get_pool()
    for attempt in (1, 2):
        try:
            with pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, params)

                    if mode == "one":
                        return cur.fetchone()
                    elif mode == "all":
                        return cur.fetchall()
                    elif mode == "rowcount":
                        return cur.rowcount or 0
                    else:
                        return None
        except psycopg.OperationalError:
            pool.reset()
            if attempt == 2:
                raise



def load_user_history_ksp(mail):
    """
    Load user's KSP games from DB (via pool) and merge into DATOTEKA_KSP.
    """
    rows = _exec_with_retry(
        """
        SELECT game_id, player, computer
        FROM ksp
        WHERE username = %s
        ORDER BY game_id
        """,
        (mail),
        mode="all"
    )

    user_games = {str(gid): [player, computer] for gid, player, computer in rows}

    # Read existing JSON (if any)
    try:
        with open(DATOTEKA_KSP, "r", encoding="utf-8") as f:
            try:
                all_data = json.load(f)
            except json.JSONDecodeError:
                all_data = {}
    except FileNotFoundError:
        all_data = {}

    existing = all_data.get(mail, {})
    existing.update(user_games)
    all_data[mail] = existing

    # Ensure folder exists
    Path(os.path.dirname(DATOTEKA_KSP) or ".").mkdir(parents=True, exist_ok=True)

    # Atomic write to avoid partial files
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tf:
        json.dump(all_data, tf, indent=2, ensure_ascii=False)
        tmp_name = tf.name
    os.replace(tmp_name, DATOTEKA_KSP)


def delete_ksp(self) -> int:
    """
    Delete all KSP games for current user (via pool + retry).
    Returns the number of deleted rows; also resets self.id to 0.
    """
    deleted = _exec_with_retry(
        "DELETE FROM ksp WHERE username = %s",
        (self.uporabnik,),
        mode="rowcount",
    )
    return int(deleted or 0)
        
#=========================================================================================================================================================




        