import psycopg2
import json
import os
from dotenv import load_dotenv
from psycopg2 import Error

load_dotenv()
# Replace the URL below with your own CockroachDB connection string
DB_URL = os.environ["DB_URL"]
DATOTEKA_KSP = 'datoteke/ksp.json'
DATOTEKA_KSPOV = 'datoteke/kspov.json'

def create_table():
    try:
        connection = psycopg2.connect(DB_URL)
        cursor = connection.cursor()

        # 2) SQL query to create a new table
        create_table_query = "CREATE TABLE IF NOT EXISTS kspov (username TEXT, game_id INT, player INT, computer INT, PRIMARY KEY (username ASC, game_id ASC));"
        cursor.execute(create_table_query)

        # 3) commit and confirm
        connection.commit()
        print("Table created successfully in CockroachDB")

    except (Exception, Error) as error:
        print("Error creating table.", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def insert_game_ksp(user):
    with open(DATOTEKA_KSP,"r", encoding="utf-8") as f:
        data = json.load(f)
    connection = psycopg2.connect(DB_URL)
    cursor = connection.cursor()

    upsert_sql = """
        INSERT INTO ksp (username, game_id, player, computer)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (username, game_id) DO UPDATE
            SET player   = EXCLUDED.player,
                computer = EXCLUDED.computer
    """
    for username, games in data.items():
        if user == username:
            for game_id_str, scores in games.items():
                game_id, player_score, computer_score = int(game_id_str), scores[0], scores[1]
                cursor.execute(upsert_sql, (username, game_id, player_score, computer_score))

    connection.commit()
    cursor.close()
    connection.close()
    print("Data loaded into ksp.")

insert_game_ksp("jano")