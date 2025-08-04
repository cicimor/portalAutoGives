import sqlite3
import os
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.db"))

def load_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, prizes_count_filter, min_volume_filter, require_boost_filter, lang FROM users')
    rows = c.fetchall()
    users = []
    for row in rows:
        users.append({
            "id": row[0],
            "prizes_count_filter": row[1],
            "min_volume_filter": row[2],
            "require_boost_filter": bool(row[3]),
            "lang": row[4] if row[4] else None
        })
    conn.close()
    return users

def get_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, prizes_count_filter, min_volume_filter, require_boost_filter, lang FROM users WHERE id=?', (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "prizes_count_filter": row[1],
            "min_volume_filter": row[2],
            "require_boost_filter": bool(row[3]),
            "lang": row[4] if row[4] else None
        }
    return None

def save_user(user):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO users (id, prizes_count_filter, min_volume_filter, require_boost_filter, lang)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            prizes_count_filter=excluded.prizes_count_filter,
            min_volume_filter=excluded.min_volume_filter,
            require_boost_filter=excluded.require_boost_filter,
            lang=excluded.lang
    ''', (
        user["id"],
        user.get("prizes_count_filter", 0),
        user.get("min_volume_filter", 999999),
        int(user.get("require_boost_filter", False)),
        user.get("lang")
    ))
    conn.commit()
    conn.close()

def delete_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE id=?', (user_id,))
    conn.commit()
    conn.close()