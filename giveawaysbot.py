import asyncio
import json
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from datetime import datetime, timezone
from db_script.mysql_conn import get_mysql_connection
import time
from gives import check_giveaways
from auto_sub import run_main_loop

from db_script.db_users import load_users, save_user, get_user, delete_user
from db_script.db_sentids import load_sent_ids_db, save_sent_ids_db



from localization import get_locale, get_lang_code, langs_keyboard, PHOTO_URLS

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "main.db"))

TOKEN = "8061740462:AAHORi-44zPNfQ4kEcsuMF9vELazz5eO2tI"
ADMIN_IDS = [999400645, 6971823973]
CHANNEL_ID =  -1002725075873

CHECK_INTERVAL = 10
semaphore = asyncio.Semaphore(30)  # До 30 параллельных сообщений


bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

class FilterStates(StatesGroup):
    waiting_for_prizes_count = State()
    waiting_for_min_volume = State()

def load_accepted_giveaways():
    conn = get_mysql_connection()

    c = conn.cursor()
    c.execute("SELECT data FROM accepted_giveaways")
    rows = c.fetchall()
    conn.close()
    return [json.loads(row[0]) for row in rows]

def load_confirmed_giveaways():
    conn = get_mysql_connection()

    c = conn.cursor()
    c.execute("SELECT data FROM confirmed_giveaways")
    rows = c.fetchall()
    conn.close()
    return [json.loads(row[0]) for row in rows]

def save_confirmed_giveaway(giveaway):
    conn = get_mysql_connection()
    c = conn.cursor()
    # Сохраняем или обновляем запись
    c.execute("""
        INSERT INTO confirmed_giveaways (id, data)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE data = VALUES(data)
    """, (giveaway["id"], json.dumps(giveaway, ensure_ascii=False)))
    conn.commit()
    conn.close()

def load_sent_ids():
    return load_sent_ids_db()

def save_sent_ids(sent_ids):
    save_sent_ids_db(sent_ids)

def get_giveaway_link(giveaway_id):
    return f"https://t.me/portals/market?startapp=gwr_{giveaway_id}_6971823973"

def format_prizes(prizes: list, prizes_count: int, lang) -> str:
    if prizes_count > 3:
        main_prizes = '\n'.join([f'• {p}' for p in prizes[:3]])
        more_templates = {
            "ru": "\nи ещё {n}!",
            "en": "\nand {n} more!",
            "pt": "\ne mais {n}!"
        }
        more_template = more_templates.get(lang, more_templates["en"])
        more = more_template.format(n=prizes_count - 3)
        return f"{main_prizes}{more}"
    else:
        return '\n'.join([f'• {p}' for p in prizes])

def get_user_filters(user):
    return (
        user.get("prizes_count_filter", 0),
        user.get("min_volume_filter", 999999),
        user.get("require_boost_filter", False)
    )

def chunked(iterable, size):
    for i in range(0, len(iterable), size):
        yield iterable[i:i+size]

@dp.message(Command("lang"))
async def choose_lang(message: types.Message):
    await message.answer(
        "🌍 Choose a language / Выберите язык / Escolha o idioma:",
        reply_markup=langs_keyboard()
    )

@dp.callback_query(F.data.in_(["lang_ru", "lang_en", "lang_pt"]))
async def set_lang_callback(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = callback.data.split("_")[1]
    user = get_user(user_id)
    is_first_time = False

    if user:
        is_first_time = not user.get("lang")
        user["lang"] = lang
    else:
        is_first_time = True
        user = {"id": user_id, "lang": lang}
        print(f"[LOG][NEW_USER] User registered: id={user_id}, lang={lang}, username={getattr(callback.from_user, 'username', None)}")

    save_user(user)
    loc = get_locale(callback.from_user, [user])
    await callback.answer()
    await callback.message.delete()
    await bot.send_message(user_id, loc["lang_set"])
    if is_first_time:
        await bot.send_message(user_id, loc["start_message"], parse_mode="HTML")
    await state.clear()

@dp.message(Command("set"))
async def set_filter_menu(message: types.Message):
    users = load_users()
    loc = get_locale(message.from_user, users)
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=loc["choose_param"][0][0], callback_data=loc["choose_param"][0][1]),
                InlineKeyboardButton(text=loc["choose_param"][1][0], callback_data=loc["choose_param"][1][1]),
            ],
            [
                InlineKeyboardButton(text=loc["choose_param"][2][0], callback_data=loc["choose_param"][2][1]),
            ]
        ]
    )
    await message.answer(loc["set_filter_menu"], reply_markup=kb)

@dp.callback_query(F.data == "set_prizes_count")
async def set_prizes_count_callback(callback: types.CallbackQuery, state: FSMContext):
    users = load_users()
    loc = get_locale(callback.from_user, users)
    await callback.message.answer(loc["enter_prizes_count"])
    await state.set_state(FilterStates.waiting_for_prizes_count)
    await callback.answer()

@dp.callback_query(F.data == "set_min_volume")
async def set_min_volume_callback(callback: types.CallbackQuery, state: FSMContext):
    users = load_users()
    loc = get_locale(callback.from_user, users)
    await callback.message.answer(loc["enter_min_volume"])
    await state.set_state(FilterStates.waiting_for_min_volume)
    await callback.answer()

@dp.callback_query(F.data == "set_boost_filter")
async def set_boost_filter_callback(callback: types.CallbackQuery, state: FSMContext):
    users = load_users()
    loc = get_locale(callback.from_user, users)
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=loc["boost_all"], callback_data="boost_all"),
                InlineKeyboardButton(text=loc["boost_no"], callback_data="boost_no"),
            ]
        ]
    )
    await callback.message.answer(loc["boost_filter_ask"], reply_markup=kb)
    await callback.answer()

@dp.callback_query(F.data.in_(["boost_all", "boost_no"]))
async def save_boost_filter(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    boost_value = callback.data == "boost_no"
    user = get_user(user_id)
    loc = get_locale(callback.from_user, [user] if user else [])
    if user:
        user["require_boost_filter"] = boost_value
    else:
        user = {
            "id": user_id,
            "prizes_count_filter": 0,
            "min_volume_filter": 999999,
            "require_boost_filter": boost_value,
            "lang": get_lang_code(callback.from_user, [user] if user else [])
        }
    save_user(user)
    answer_text = loc["boost_filter_set_no"] if boost_value else loc["boost_filter_set_all"]
    await callback.message.answer(answer_text)
    await callback.answer()

@dp.message(FilterStates.waiting_for_prizes_count)
async def set_prizes_count(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = get_user(user_id)
    loc = get_locale(message.from_user, [user] if user else [])
    try:
        value = int(message.text)
    except ValueError:
        await message.answer(loc["please_enter_number"])
        return
    if value > 50:
        await message.answer(loc["max_prizes"])
        return
    await state.update_data(prizes_count=value)
    data = await state.get_data()
    if user:
        user["prizes_count_filter"] = data["prizes_count"]
    else:
        user = {"id": user_id, "prizes_count_filter": data["prizes_count"], "lang": get_lang_code(message.from_user, [user] if user else [])}
    save_user(user)
    await message.answer(loc["filter_saved"])
    await state.clear()

@dp.message(FilterStates.waiting_for_min_volume)
async def set_min_volume(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = get_user(user_id)
    loc = get_locale(message.from_user, [user] if user else [])
    try:
        value = int(message.text)
    except ValueError:
        await message.answer(loc["please_enter_number"])
        return
    data = await state.get_data()
    if user:
        user["min_volume_filter"] = value
    else:
        user = {"id": user_id, "min_volume_filter": value, "lang": get_lang_code(message.from_user, [user] if user else [])}
    save_user(user)
    await message.answer(loc["filter_saved"])
    await state.clear()

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = get_user(user_id)
    if not user or "lang" not in user or not user["lang"]:
        kb = langs_keyboard()
        await message.answer("🌍 Choose a language / Выберите язык / Escolha o idioma:", reply_markup=kb)
        if not user:
            save_user({"id": user_id})
            print(f"[LOG][NEW_USER] User registered: id={user_id}, lang=None, username={getattr(message.from_user, 'username', None)}")
        await state.clear()
        return

    loc = get_locale(message.from_user, [user])
    await message.answer(loc["start_message"], parse_mode="HTML")

async def notify_channel(giveaway):
    ends_at = giveaway.get("ends_at")
    reqpremium = giveaway.get("require_premium")
    reqboost = giveaway.get("require_boost")
    time_days, time_hours, time_min = None, None, None
    if ends_at:
        try:
            end_dt = datetime.fromisoformat(ends_at.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            delta = end_dt - now
            total_seconds = int(delta.total_seconds())
            days = delta.days
            hours = (total_seconds // 3600) % 24
            minutes = (total_seconds // 60) % 60
            time_days, time_hours, time_min = days, hours, minutes
        except Exception as ex:
            print(f"Ошибка при вычислении оставшегося времени до конца розыгрыша: {ex}")

    lang = "en"  # Можно сделать динамически, если нужно
    users = load_users()
    loc = get_locale(CHANNEL_ID, users)
    prizes_text = format_prizes(giveaway["prizes"], giveaway["prizes_count"], lang)
    channel_text = loc["join_giveaway_ch"].format(
        prizes=prizes_text,
        require_premium='Yes' if reqpremium else 'NO',
        require_boost='YES' if reqboost else 'NO',
        timeD=time_days,
        timeH=time_hours,
        timeM=time_min
    )
    kb_channel = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=loc["giveaway_link"], url=get_giveaway_link(giveaway["id"]))]
        ]
    )
    photo_url_channel = PHOTO_URLS.get(lang, PHOTO_URLS["en"])
    try:
        if photo_url_channel:
            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=photo_url_channel,
                caption=channel_text,
                parse_mode="HTML",
                reply_markup=kb_channel
            )
        else:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=channel_text,
                parse_mode="HTML",
                reply_markup=kb_channel
            )
        print(f"[LOG][CHANNEL] Сообщение отправлено в канал {CHANNEL_ID}")
    except Exception as e:
        print(f"[ERROR] Не удалось отправить сообщение в канал: {e}")

async def notify_admins(giveaways):
    sent_giveaway_ids = load_sent_ids_db()
    new_giveaways = [g for g in giveaways if g['id'] not in sent_giveaway_ids]
    for g in new_giveaways:
        for admin_id in ADMIN_IDS:
            loc = get_locale(admin_id)
            kb = InlineKeyboardBuilder()
            kb.button(
                text=loc["confirm_participate"],
                callback_data=f"confirm:{g['id']}"
            )
            kb.button(
                text=loc["giveaway_link"],
                url=get_giveaway_link(g['id'])
            )
            text = (
                f"{loc['need_confirm']}"
                f"{loc['id'].format(id=g['id'])}"
                f"{loc['prizes'].format(prizes=', '.join(g['prizes']))}"
                f"{loc['require_premium'].format(premium='Да' if g['require_premium'] else 'Нет') if loc['lang_name']=='Русский' else ('Sim' if g['require_premium'] else 'Não') if loc['lang_name']=='Português' else ('Yes' if g['require_premium'] else 'No')}"
                f"\n"
                f"{loc['require_boost'].format(boost='Да' if g['require_boost'] else 'Нет') if loc['lang_name']=='Русский' else ('Sim' if g['require_boost'] else 'Não') if loc['lang_name']=='Português' else ('Yes' if g['require_boost'] else 'No')}"
                f"\n"
                f"{loc['min_volume'].format(min_vol=g['min_volume'])}"
            )
            await bot.send_message(admin_id, text, reply_markup=kb.as_markup())
        sent_giveaway_ids.add(g['id'])
        await notify_channel(g)
    save_sent_ids_db(sent_giveaway_ids)


async def check_user_eligible(user, giveaway):
    """Проверка, подходит ли пользователь под условия розыгрыша."""
    prizes_count_filter, min_volume_filter, require_boost_filter = get_user_filters(user)

    if giveaway["prizes_count"] < prizes_count_filter:
        return None

    try:
        min_volume = int(giveaway.get("min_volume", "0"))
    except:
        min_volume = 0

    if min_volume > min_volume_filter:
        return None

    if require_boost_filter and giveaway.get("require_boost", False):
        return None

    try:
        async with semaphore:
            chat = await bot.get_chat_member(user["id"], user["id"])
        is_premium = getattr(chat.user, "is_premium", False)
    except Exception:
        is_premium = False

    if giveaway.get("require_premium") and not is_premium:
        return None

    return user  # пользователь подходит



async def notify_users(giveaway, throttle_per_sec=30):
    from datetime import datetime, timezone
    ends_at = giveaway.get("ends_at")
    time_days, time_hours, time_min = None, None, None
    if ends_at:
        try:
            end_dt = datetime.fromisoformat(ends_at.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            delta = end_dt - now
            total_seconds = int(delta.total_seconds())
            days = delta.days
            hours = (total_seconds // 3600) % 24
            minutes = (total_seconds // 60) % 60
            time_days, time_hours, time_min = days, hours, minutes
        except Exception as ex:
            print(f"Ошибка при вычислении времени: {ex}")

    users = load_users()

    # 🔁 Параллельно проверяем, кто подходит
    check_tasks = [check_user_eligible(user, giveaway) for user in users]
    results = await asyncio.gather(*check_tasks)
    eligible_users = [user for user in results if user is not None]

    # 📤 Рассылаем подходящим пользователям
    total_sent = 0
    batch = []
    t0 = time.time()
    for user in eligible_users:
        lang = user.get("lang", "ru")
        loc = get_locale(user["id"], users)
        prizes_text = format_prizes(giveaway["prizes"], giveaway["prizes_count"], lang)

        text = loc["join_giveaway"].format(
            prizes=prizes_text,
            timeD=time_days,
            timeH=time_hours,
            timeM=time_min
        )
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=loc["giveaway_link"], url=get_giveaway_link(giveaway["id"]))],
                [InlineKeyboardButton(text=loc["before_giveaway"], url="https://t.me/PortAwayAll")]
            ]
        )
        photo_url = PHOTO_URLS.get(lang, PHOTO_URLS["en"])
        batch.append((user["id"], text, kb, photo_url))

        if len(batch) >= throttle_per_sec:
            await _send_batch(batch)
            total_sent += len(batch)
            batch.clear()
            time.sleep(1)

    # Отправляем оставшиеся
    if batch:
        await _send_batch(batch)
        total_sent += len(batch)
    t1 = time.time()
    t = t1-t0
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                f"✅ Рассылка завершена.\nВсего отправлено: <b>{total_sent}</b> сообщений.",
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"[ERROR] Не удалось отправить сообщение админу {admin_id}: {e}")

    print(f"[LOG][DONE] Рассылка завершена: отправлено {total_sent} сообщений.\nпрошло {t} секунд")

    
async def send_one(user_id, text, kb, photo_url):
    async with semaphore:
        try:
            if photo_url:
                await bot.send_photo(
                    chat_id=user_id,
                    photo=photo_url,
                    caption=text,
                    parse_mode="HTML",
                    reply_markup=kb
                )
            else:
                await bot.send_message(
                    chat_id=user_id,
                    text=text,
                    parse_mode="HTML",
                    reply_markup=kb
                )
        except TelegramForbiddenError:
            print(f"Пользователь {user_id} удалён (TelegramForbiddenError).")
            delete_user(user_id)
            return user_id
        except TelegramBadRequest as e:
            if "chat not found" in str(e).lower():
                print(f"Пользователь {user_id} удалён (chat not found).")
                delete_user(user_id)
                return user_id
            print(f"Send error {user_id}: {e}")
        except Exception as e:
            if "chat not found" in str(e).lower() or "bot was blocked" in str(e).lower():
                print(f"Пользователь {user_id} удалён (bot blocked).")
                delete_user(user_id)
                return user_id
            print(f"Send error {user_id}: {e}")
        else:
            print(f"[LOG][SEND] Sent text message to user_id={user_id}")
    return None

async def _send_batch(batch):
    tasks = [send_one(user_id, text, kb, photo_url) for user_id, text, kb, photo_url in batch]
    await asyncio.gather(*tasks)

@dp.callback_query(F.data.startswith("confirm:"))
async def admin_confirm(callback: types.CallbackQuery):
    try:
        giveaway_id = callback.data.split(":")[1]
        all_giveaways = load_accepted_giveaways()
        confirmed = load_confirmed_giveaways()
        to_confirm = [g for g in all_giveaways if g["id"] == giveaway_id]
        user = get_user(callback.from_user.id)
        loc = get_locale(callback.from_user, [user] if user else [])
        print("+")
        if not to_confirm:
            await callback.answer(loc["not_found"], show_alert=True)
            print("+")
            return
        for g in to_confirm:
            if not any(c["id"] == g["id"] for c in confirmed):
                save_confirmed_giveaway(g)
                print("+")  # Сохраняем в БД
        await callback.answer(loc["confirmed"])
        await callback.message.delete()

        for g in to_confirm:
            print("+")
            try:
                await notify_users(g)
            except Exception as e:
                print(f"❌ Error inside notify_users: {type(e).__name__} — {repr(e)}")
                print(f"Offending giveaway object: {g}")
    except Exception as e:
        user = get_user(callback.from_user.id)
        loc = get_locale(callback.from_user, [user] if user else [])
        await callback.answer(loc["error"].format(err=repr(e)), show_alert=True)
        print(f"Error in confirm handler: {type(e).__name__} — {repr(e)}")


last_checked_ids = set()

async def db_watcher():
    global last_checked_ids
    while True:
        try:
            giveaways = load_accepted_giveaways()
            current_ids = {g['id'] for g in giveaways}
            if current_ids != last_checked_ids:
                last_checked_ids = current_ids
                await notify_admins(giveaways)
        except Exception as e:
            print(f"DB reading error: {e}")
        await asyncio.sleep(CHECK_INTERVAL)

async def main():
    asyncio.create_task(db_watcher())
    await dp.start_polling(bot)

async def start_all():
    await asyncio.gather(
        check_giveaways(),
        run_main_loop(),
        main()
    )

if __name__ == "__main__":
    asyncio.run(start_all())