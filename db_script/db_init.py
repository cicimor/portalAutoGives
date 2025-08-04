import sqlite3
import os
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.db"))

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            prizes_count_filter INTEGER DEFAULT 0,
            min_volume_filter INTEGER DEFAULT 999999,
            require_boost_filter INTEGER DEFAULT 0,
            lang TEXT
        )
    ''')
    c.execute("""
        CREATE TABLE IF NOT EXISTS giveaways (
            id TEXT PRIMARY KEY,
            data TEXT,
            created_at TEXT
        )
    """)
    c.execute("DROP TABLE IF EXISTS new_giveaways")
    c.execute("""
    CREATE TABLE new_giveaways (
        id TEXT PRIMARY KEY,
        data TEXT,
        detected_at TEXT
    )
    """)
    c.execute('''
        CREATE TABLE IF NOT EXISTS accepted_giveaways (
            id TEXT PRIMARY KEY,
            data TEXT,
            accepted_at TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS confirmed_giveaways (
            id TEXT PRIMARY KEY,
            data TEXT,
            confirmed_at TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS sent_giveaway_ids (
            giveaway_id TEXT PRIMARY KEY
        )
    ''')
    conn.commit()
    conn.close()
