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

def insert_game_ksp(mail, game_id, player_score, computer_score) -> int:
    sql = """
    INSERT INTO ksp (username, game_id, player, computer, played_at)
    VALUES (%s, %s, %s, %s, NOW())
    ON CONFLICT (username, game_id) DO UPDATE
      SET player   = EXCLUDED.player,
          computer = EXCLUDED.computer,
          played_at = NOW()
    """
    return _exec_with_retry(sql, (mail, game_id, player_score, computer_score), mode="rowcount")

def get_id_ksp(mail):
    row = _exec_with_retry(
        """
        SELECT COALESCE(MAX(game_id::int), 0) FROM ksp WHERE username = %s 
        """,
        (mail,),
        mode="one",
    )
    max_id = row[0] if row else 0
    return int(max_id)

def get_user_history_ksp_list(mail):
    rows = _exec_with_retry(
        """
        SELECT game_id, player, computer
        FROM ksp
        WHERE username = %s
        ORDER BY game_id
        """,
        (mail,),                 # tuple!
        mode="all",
    )

    return [{"game_id": int(g), "player": int(p), "computer": int(c)} for (g, p, c) in rows]

def delete_ksp(mail) -> int:
    """
    Delete all KSP games for current user (via pool + retry).
    Returns the number of deleted rows; also resets self.id to 0.
    """
    deleted = _exec_with_retry(
        "DELETE FROM ksp WHERE username = %s",
        (mail,),
        mode="rowcount",
    )
    return int(deleted or 0)
        
#=========================================================================================================================================================

def insert_game_kspov(mail, game_id, player_score, computer_score) -> int:
    sql = """
    INSERT INTO kspov (username, game_id, player, computer, played_at)
    VALUES (%s, %s, %s, %s, NOW())
    ON CONFLICT (username, game_id) DO UPDATE
      SET player   = EXCLUDED.player,
          computer = EXCLUDED.computer,
          played_at = NOW()
    """
    return _exec_with_retry(sql, (mail, game_id, player_score, computer_score), mode="rowcount")

def get_id_kspov(mail):
    row = _exec_with_retry(
        """
        SELECT COALESCE(MAX(game_id::int), 0) FROM kspov WHERE username = %s 
        """,
        (mail,),
        mode="one",
    )
    max_id = row[0] if row else 0
    return int(max_id)



        