import requests
import json
import os
import time
import sqlite3
from datetime import datetime,timezone
from db_script.db_init import init_db
import asyncio

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "main.db"))


def fetch_all_giveaways(headers):
    url = f"https://portals-market.com/api/giveaways/?offset=0&limit=2000&status=active"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    results = data.get("giveaways", [])
    all_results = results
    return all_results

def join_gives(headers):
    url = f"https://portals-market.com/api/giveaways/participations?offset=0&limit=250&status=active"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    results = data.get("participations", [])
    return results

def get_existing_ids(conn):
    c = conn.cursor()
    c.execute("SELECT data FROM giveaways")
    rows = c.fetchall()
    return set(row[0] for row in rows)

def clear_old_giveaways(conn):
    c = conn.cursor()
    c.execute("DELETE FROM giveaways")
    conn.commit()

def clear_new_giveaways(conn):
    c = conn.cursor()
    c.execute("DELETE FROM new_giveaways")
    conn.commit()

def insert_all_giveaways(conn, giveaways):
    c = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()  

    for item in giveaways:
        c.execute(
            "INSERT INTO giveaways (id, data, created_at) VALUES (?, ?, ?)",
            (item["id"], json.dumps(item, ensure_ascii=False), now)
        )
    conn.commit()

def insert_new_giveaways(conn, giveaways):
    if not giveaways:
        return
    c = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()  

    for item in giveaways:
        c.execute(
            "INSERT INTO new_giveaways (id, data, detected_at) VALUES (?, ?, ?)",
            (item["id"], json.dumps(item, ensure_ascii=False), now)
        )
    conn.commit()

async def check_giveaways():
    while  True:

        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "authorization": "tma user=%7B%22id%22%3A6971823973%2C%22first_name%22%3A%22%5C%2F%5C%2F%5C%2F%5C%5C%5C%5C%5C%5C%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22tonslayer%22%2C%22language_code%22%3A%22ru%22%2C%22is_premium%22%3Atrue%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FUa0p1LXPBauSvAuMzcXYGtWY91lpD7pYbdGVQB8MkqRPeRvWYU_j3v0OaLCFNSM2.svg%22%7D&chat_instance=-4053137774363921894&chat_type=private&start_param=gwr_e51a34ed-2414-4598-9a7c-41f5f6c467cf_6971823973&auth_date=1753554371&signature=K6QZJkO2s8uW5PyVpqv7aQ_RfSx9HuYJe8Z8JxBz9Jy9_j0-MyZBZdRSHLBnADMWs0KBJAig38NKkx-1g3qyAg&hash=d8d4e21e440df327f1a7a24699945d2f23becf49b7da6fb0808fc25cefc05a66",
            "cookie": "_ym_uid=1752688918123731692; _ym_d=1752688918; _ym_isad=2; _ym_visorc=b",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        }

        try:
            conn = sqlite3.connect(DB_PATH)
            new_data = join_gives(headers)
            all_data = fetch_all_giveaways(headers)
            filtered_data = [item for item in all_data if item.get("participants_count", 0) > 0]

            existing_ids = get_existing_ids(conn)
            joinGives = [item.get("id") for item in new_data if "id" in item]
            print("+")
            new_only = []
            for item in existing_ids:
                item_dict = json.loads(item)
                if item_dict["id"] not in joinGives:
                    new_only.append(item)

            new_only = [json.loads(item) for item in new_only]
        

            

        
        



        # Очистка таблицы новых перед вставкой
            clear_new_giveaways(conn)
            insert_new_giveaways(conn, new_only)

        # Полная перезапись актуальных розыгрышей
            clear_old_giveaways(conn)
            insert_all_giveaways(conn, filtered_data)

            if new_only:
                print(f"[{datetime.now()}] 🆕 Новых розыгрышей: {len(new_only)}")
            else:
                print(f"[{datetime.now()}] ℹ️ Новых розыгрышей нет.")

            conn.close()

        except requests.exceptions.RequestException as e:
            print(f"[{datetime.now()}] ❌ HTTP ошибка: {e}")
        except Exception as e:
            print(f"[{datetime.now()}] ❌ Ошибка: {e}")
        await asyncio.sleep(600)

if __name__ == "__main__":
    init_db()  # Убедись, что таблицы есть
    
    check_giveaways()  # каждые полчаса
