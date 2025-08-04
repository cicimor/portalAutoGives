from db_script.mysql_conn import get_mysql_connection

def load_users():
    conn = get_mysql_connection()
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
    conn = get_mysql_connection()
    c = conn.cursor()
    c.execute('SELECT id, prizes_count_filter, min_volume_filter, require_boost_filter, lang FROM users WHERE id=%s', (user_id,))
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
    conn = get_mysql_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO users (id, prizes_count_filter, min_volume_filter, require_boost_filter, lang)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            prizes_count_filter = VALUES(prizes_count_filter),
            min_volume_filter = VALUES(min_volume_filter),
            require_boost_filter = VALUES(require_boost_filter),
            lang = VALUES(lang)
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
    conn = get_mysql_connection()
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE id=%s', (user_id,))
    conn.commit()
    conn.close()
