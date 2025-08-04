from db_script.mysql_conn import get_mysql_connection

def load_sent_ids_db():
    conn = get_mysql_connection()
    c = conn.cursor()
    c.execute("SELECT giveaway_id FROM sent_giveaway_ids")
    rows = c.fetchall()
    conn.close()
    return set(row[0] for row in rows)

def save_sent_ids_db(sent_ids):
    conn = get_mysql_connection()
    c = conn.cursor()
    # Очищаем таблицу перед вставкой
    c.execute("DELETE FROM sent_giveaway_ids")
    # Вставляем новые значения
    c.executemany(
        "INSERT IGNORE INTO sent_giveaway_ids (giveaway_id) VALUES (%s)",
        [(giveaway_id,) for giveaway_id in sent_ids]
    )
    conn.commit()
    conn.close()
