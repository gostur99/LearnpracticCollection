import os
import sqlite3

DB_FILE = "collection.db"
INIT_SQL_FILE = "init.sql"

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    if os.path.exists(DB_FILE):
        return
    if not os.path.exists(INIT_SQL_FILE):
        raise FileNotFoundError(f"Файл '{INIT_SQL_FILE}' не найден!")
    with open(INIT_SQL_FILE, "r", encoding="utf-8") as f:
        sql_script = f.read()
    with get_connection() as conn:
        conn.executescript(sql_script)
        conn.commit()

def reset_db() -> None:
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    init_db()