import os
import json
import asyncio
import time
import re
from telethon import TelegramClient, functions, errors
from datetime import datetime,timezone,UTC
import requests
from db_script.mysql_conn import get_mysql_connection


# 📱 Данные вашего Telegram приложения
api_id = 25064132
api_hash = 'c8e7a6dc03fcda7986a19a0b797466f0'
phone_number = '+375296285767'



headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "authorization": "tma user=%7B%22id%22%3A6971823973%2C%22first_name%22%3A%22%5C%2F%5C%2F%5C%2F%5C%5C%5C%5C%5C%5C%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22tonslayer%22%2C%22language_code%22%3A%22ru%22%2C%22is_premium%22%3Atrue%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FUa0p1LXPBauSvAuMzcXYGtWY91lpD7pYbdGVQB8MkqRPeRvWYU_j3v0OaLCFNSM2.svg%22%7D&chat_instance=-4053137774363921894&chat_type=private&start_param=gwr_12c784cc-035e-4132-92a1-069a688a16c0_6971823973&auth_date=1753385831&signature=RUEsPz-G73_p2NqVAJ7hGElut-CUfoca02mFcVOJO1Qw9stxqZe__z1Yvcyl7yLHmMcivzPC_5pUxPAtdLWrBg&hash=77c69941b9b8f2008c5435d8a8d56b001d1988d8ea13972e197d499c4756a32b",
    "cookie": "_ym_uid=1752688918123731692; _ym_d=1752688918; _ym_isad=2; _ym_visorc=w",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
}

# 🗂 Название файла с розыгрышами


# 🤖 Инициализация Telethon-клиента
client = TelegramClient('portal_session', api_id, api_hash)

# 📌 Храним список уже подписанных каналов и обработанные конкурсы



subscribed_channels = set()




def accepted_giveaway_ids():
    conn = get_mysql_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM accepted_giveaways")
    rows = c.fetchall()
    conn.close()
    return set(row[0] for row in rows)

def get_new_channels_and_giveaways():
    conn = get_mysql_connection()
    c = conn.cursor()
    c.execute("SELECT id, data FROM new_giveaways")
    rows = c.fetchall()
    conn.close()

    new_channels = []
    id_to_giveaway = {}

    for row in rows:
        giveaway_id, data_json = row
        try:
            giveaway = json.loads(data_json)
        except json.JSONDecodeError:
            continue

        id_to_giveaway[giveaway_id] = giveaway
        channels = giveaway.get("channels", [])
        for channel in channels:
            username = channel.get("username")
            if username and username not in subscribed_channels:
                new_channels.append((username, giveaway_id))

    return new_channels, id_to_giveaway



def save_accepted_giveaway_to_db(giveaway):
    conn = get_mysql_connection()
    c = conn.cursor()

    prizes = []
    for prize in giveaway.get("prizes", []):
        nft_name = prize.get("nft_name")
        nft_num = prize.get("nft_external_collection_number")
        if nft_name and nft_num is not None:
            prizes.append(f"{nft_name} #{nft_num}")

    data = {
        "id": giveaway.get("id"),
        "require_premium": giveaway.get("require_premium"),
        "require_boost": giveaway.get("require_boost"),
        "min_volume": giveaway.get("min_volume"),
        "participants_count": giveaway.get("participants_count"),
        "prizes_count": giveaway.get("prizes_count"),
        "prizes": prizes,
        "ends_at": giveaway.get("ends_at"),
        "chanels": giveaway.get("channels")
    }

    try:
        c.execute("""
            INSERT IGNORE INTO accepted_giveaways (id, data, accepted_at)
            VALUES (%s, %s, %s)
        """, (data["id"], json.dumps(data, ensure_ascii=False), datetime.now(UTC).isoformat()))
        conn.commit()
    except Exception as e:
        print(f"❌ Ошибка при сохранении розыгрыша {data['id']} в БД: {e}")
    finally:
        conn.close()

def extract_wait_time(error_msg):
    match = re.search(r'(\d+) seconds', error_msg)
    return int(match.group(1)) if match else 60

async def handle_leave_channel(username):
    try:
        result = await client(functions.channels.LeaveChannelRequest(username))
        print(f"✅ Отписан от @{username}")
        return True
    except Exception as e:
        print(f"❌ Ошибка при отписке от @{username}: {e}")
        return False

# 🆕 Функция для обработки подачи заявки на вступление
async def handle_join_request(username):
    try:
        result = await client(functions.channels.JoinChannelRequest(username))
        print(f"✅ Подписан на @{username}")
        return True

    except errors.InviteRequestSentError:
        print('скип')
        return False
    except errors.UserAlreadyParticipantError:
        print(f"⚠️ Уже в канале @{username} (по исключению)")
        return True
    except Exception as e:
        if "A wait of" in str(e):
            wait_seconds = extract_wait_time(str(e))
            print(f"⏳ Telegram требует подождать {wait_seconds} секунд...")
            await asyncio.sleep(wait_seconds)
        else:
            print(f"❌ Ошибка при подписке/подаче заявки на @{username}: {e}")
        return False

async def monitor_and_subscribe():
    print("🚀 Старт подписки...")
    giveaway_counter = 0
    while True:
        try:
            new_channels, id_to_giveaway = get_new_channels_and_giveaways()
            channels_by_giveaway = {}
            for username, giveaway_id in new_channels:
                channels_by_giveaway.setdefault(giveaway_id, []).append(username)

            if new_channels:
                for giveaway_id, usernames in channels_by_giveaway.items():
                    all_success = True
                    for username in usernames:
                        print(f"▶ Подписка/заявка на: @{username}")
                        
                        success = await handle_join_request(username)
                        if success:
                            subscribed_channels.add(username)
                        else:
                            all_success = False
                            subscribed_channels.add(username)
        
                        await asyncio.sleep(60)
                    if all_success and giveaway_id and giveaway_id not in accepted_giveaway_ids():
                        url = f"https://portals-market.com/api/giveaways/{giveaway_id}/join"
                        save_accepted_giveaway_to_db(id_to_giveaway[giveaway_id])
                        
                        response = requests.post(url, headers=headers)
                        print("Response JSON:", response.json() if response.headers.get("Content-Type") == "application/json" else response.text)
                        giveaway_counter += 1
                        print(f"📝 Розыгрыш {giveaway_id} добавлен в БД ")
                         # После добавления розыгрыша — отписываемся от каналов
                        for username in usernames:
                            await handle_leave_channel(username)
                            subscribed_channels.discard(username)
                            await asyncio.sleep(60)  # удаляем из множества подписанных
                        if giveaway_counter % 10 == 0:
                            print("⏸ Достигнуто 10 розыгрышей. Пауза 5 минут...")
                            await asyncio.sleep(300)
            else:
                print("🔁 Нет новых каналов для подписки.")
            await asyncio.sleep(30)
        except Exception as e:
            print(f"\n\n[RESTART] Ошибка: {e}\nОжидание 60 секунд перед перезапуском...\n")
            await asyncio.sleep(60)

async def run_main_loop():
    while True:
        try:
            async with client:
                await monitor_and_subscribe()
        except Exception as e:
            print(f"\n\n[GLOBAL RESTART] Ошибка: {e}\nОжидание 60 секунд перед глобальным перезапуском...\n")
            await asyncio.sleep(60)

if __name__ == "__main__":
    run_main_loop()