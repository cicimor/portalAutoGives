import sqlite3
import os
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.db"))

def load_sent_ids_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT giveaway_id FROM sent_giveaway_ids")
    rows = c.fetchall()
    conn.close()
    return set(row[0] for row in rows)

def save_sent_ids_db(sent_ids):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM sent_giveaway_ids")  # Очистка перед вставкой
    c.executemany(
        "INSERT OR IGNORE INTO sent_giveaway_ids (giveaway_id) VALUES (?)",
        [(giveaway_id,) for giveaway_id in sent_ids]
    )
    conn.commit()
    conn.close()