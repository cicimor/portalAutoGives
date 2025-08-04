# localization.py

RU = {
    "lang_name": "Русский",
    "choose_lang": "🌍 Выберите язык / Choose a language / Escolha o idioma:",
    "lang_set": "Язык установлен на русский 🇷🇺",
    "start_message": (
        "🎉 Вас приветствует <b>PortAway</b> — бот автоматической рассылки 🎁 раздач из <b>Portals</b> с фильтрацией!\n\n"
        "⚙️ Для настройки фильтров отправьте команду /set"
    ),
    "set_filter_menu": "⚙️Настройка фильтра:\n\n🔧 Выберите, какой параметр хотите изменить: ",
    "choose_param": [
        ["Количество призов 🎁", "set_prizes_count"],
        ["Торговый объем 💵", "set_min_volume"],
        ["Буст канала 🚀", "set_boost_filter"],
    ],
    "enter_prizes_count": "Введите минимальное количество призов в розыгрыше (например: 1):",
    "enter_min_volume": "Ваш торговый объем",
    "boost_filter_ask": "Показывать все розыгрыши или только те, где не требуется буст?",
    "boost_all": "Все розыгрыши",
    "boost_no": "Не требующие буста",
    "boost_filter_set_no": "Теперь вы будете получать только розыгрыши без буста. ✅",
    "boost_filter_set_all": "Теперь вы будете получать все розыгрыши (и с бустом, и без). 📬",
    "please_enter_number": "Пожалуйста, введите число.",
    "max_prizes": "Максимальное число призов — 50. Пожалуйста, введите число не больше 50.",
    "filter_saved": "Настройки фильтра сохранены! ✅",
    "need_confirm": "Нужно подтвердить участие\n",
    "id": "<b>ID:</b> <code>{id}</code>\n",
    "prizes": "<b>Призы:</b> {prizes}\n",
    "require_premium": "<b>Требует премиум:</b> {premium}\n",
    "require_boost": "<b>Требует boost:</b> {boost}\n",
    "min_volume": "<b>Минимальный объем:</b> {min_vol}",
    "confirm_participate": "Подтвердить участие",
    "giveaway_link": "Ссылка на розыгрыш",
    "confirmed": "Подтверждено!",
    "not_found": "Не найдено",
    "error": "Ошибка: {err}",
    "join_giveaway": "<b>Присоединяйтесь к розыгрышу!</b>\n\n🏆 <b>Призы:</b>\n{prizes}\n До конца {timeD}д {timeH}ч {timeM}мин",
    "lang_ru": "🇷🇺 Русский",
    "lang_en": "🇬🇧 English",
    "lang_pt": "🇧🇷 Português",
    "lang_set_success": "Язык успешно изменён!",
    "before_giveaway":"Предыдущие розыгрыши"
}

EN = {
    "lang_name": "English",
    "choose_lang": "🌍 Choose a language / Выберите язык / Escolha o idioma:",
    "lang_set": "Language set to English 🇬🇧",
    "start_message": (
        "🎉 Welcome to <b>PortAway</b> — an automatic giveaway notifier bot for <b>Portals</b> with filters!\n\n"
        "⚙️ Use /set to configure your filters"
    ),
    "set_filter_menu": "⚙️Filter settings:\n\n🔧 Choose a parameter to change: ",
    "choose_param": [
        ["Number of prizes 🎁", "set_prizes_count"],
        ["Trading volume 💵", "set_min_volume"],
        ["Channel boost 🚀", "set_boost_filter"],
    ],
    "enter_prizes_count": "Enter the minimum number of prizes in the giveaway (e.g.: 1):",
    "enter_min_volume": "Your trading volume",
    "boost_filter_ask": "Show all giveaways or only those not requiring boost?",
    "boost_all": "All giveaways",
    "boost_no": "No boost required",
    "boost_filter_set_no": "You will now only receive giveaways that do not require boost. ✅",
    "boost_filter_set_all": "You will now receive all giveaways (with and without boost). 📬",
    "please_enter_number": "Please enter a number.",
    "max_prizes": "The maximum number of prizes is 50. Please enter a number no greater than 50.",
    "filter_saved": "Filter settings saved! ✅",
    "need_confirm": "Confirmation required\n",
    "id": "<b>ID:</b> <code>{id}</code>\n",
    "prizes": "<b>Prizes:</b> {prizes}\n",
    "require_premium": "<b>Premium required:</b> {premium}\n",
    "require_boost": "<b>Boost required:</b> {boost}\n",
    "min_volume": "<b>Minimum volume:</b> {min_vol}",
    "confirm_participate": "Confirm participation",
    "giveaway_link": "Giveaway link",
    "confirmed": "Confirmed!",
    "not_found": "Not found",
    "error": "Error: {err}",
    "join_giveaway": "<b>Join This Giveaway!</b>\n\n🏆 <b>Prizes:</b>\n{prizes}\n{timeD}d {timeH}h {timeM}m left",
    "join_giveaway_ch": "<b>Join This giveaway!</b>\n\n🏆 <b>Prizes:</b>\n{prizes}\n{timeD}d {timeH}h {timeM}m letft\nPremium required: {require_premium}\nBoost required: {require_premium}",
    "lang_ru": "🇷🇺 Русский",
    "lang_en": "🇬🇧 English",
    "lang_pt": "🇧🇷 Português",
    "lang_set_success": "Language changed successfully!",
    "before_giveaway":"Previous giveaways"
}

PT = {
    "lang_name": "Português",
    "choose_lang": "🌍 Escolha o idioma / Choose a language / Выберите язык:",
    "lang_set": "Idioma definido para português 🇧🇷",
    "start_message": (
        "🎉 Bem-vindo ao <b>PortAway</b> — bot de notificações automáticas de sorteios do <b>Portals</b> com filtros!\n\n"
        "⚙️ Use /set para configurar seus filtros"
    ),
    "set_filter_menu": "⚙️Configuração de filtro:\n\n🔧 Escolha um parâmetro para alterar: ",
    "choose_param": [
        ["Quantidade de prêmios 🎁", "set_prizes_count"],
        ["Volume de negociação 💵", "set_min_volume"],
        ["Boost do canal 🚀", "set_boost_filter"],
    ],
    "enter_prizes_count": "Digite o número mínimo de prêmios no sorteio (ex: 1):",
    "enter_min_volume": "Seu volume de negociação",
    "boost_filter_ask": "Mostrar todos os sorteios ou apenas os que não exigem boost?",
    "boost_all": "Todos sorteios",
    "boost_no": "Sem boost",
    "boost_filter_set_no": "Agora você só receberá sorteios que não exigem boost. ✅",
    "boost_filter_set_all": "Agora você receberá todos os sorteios (com e sem boost). 📬",
    "please_enter_number": "Por favor, digite um número.",
    "max_prizes": "O número máximo de prêmios é 50. Por favor, insira um número que não seja maior que 50.",
    "filter_saved": "Configurações de filtro salvas! ✅",
    "need_confirm": "Confirmação necessária\n",
    "id": "<b>ID:</b> <code>{id}</code>\n",
    "prizes": "<b>Prêmios:</b> {prizes}\n",
    "require_premium": "<b>Premium necessário:</b> {premium}\n",
    "require_boost": "<b>Boost necessário:</b> {boost}\n",
    "min_volume": "<b>Volume mínimo:</b> {min_vol}",
    "confirm_participate": "Confirmar participação",
    "giveaway_link": "Link do sorteio",
    "confirmed": "Confirmado!",
    "not_found": "Não encontrado",
    "error": "Erro: {err}",
    "join_giveaway": "<b>Participe do Sorteio!</b>\n\n🏆 <b>Prêmios:</b>\n{prizes}\nFaltam {timeD}d {timeH}h {timeM}min",
    "lang_ru": "🇷🇺 Русский",
    "lang_en": "🇬🇧 English",
    "lang_pt": "🇧🇷 Português",
    "lang_set_success": "Idioma alterado com sucesso!",
    "before_giveaway": "Sorteios passados"
}

LANGS = {
    "ru": RU,
    "en": EN,
    "pt": PT,
}

PHOTO_URLS = {
    "ru": "https://i.postimg.cc/xdqxqYGB/photo-2025-07-20-04-29-54.jpg",
    "en": "https://i.postimg.cc/FHTC91Sj/photo-2025-07-20-04-28-28.jpg",
    "pt": "https://i.postimg.cc/yYzbjMBS/photo-2025-07-20-04-28-37.jpg"
}

def get_locale(user, users=None):
    user_id = user.id if hasattr(user, "id") else user
    if users:
        for u in users:
            if u["id"] == user_id and "lang" in u:
                return LANGS.get(u["lang"], EN)
    lang_code = getattr(user, "language_code", "en")
    if lang_code.startswith("en"):
        return EN
    if lang_code.startswith("pt"):
        return PT
    return EN

def get_lang_code(user, users=None):
    user_id = user.id if hasattr(user, "id") else user
    if users:
        for u in users:
            if u["id"] == user_id and "lang" in u:
                return u["lang"]
    lang_code = getattr(user, "language_code", "en")
    if lang_code.startswith("en"):
        return "en"
    if lang_code.startswith("pt"):
        return "pt"
    return "en"

def langs_keyboard():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=RU["lang_ru"], callback_data="lang_ru"),
                InlineKeyboardButton(text=EN["lang_en"], callback_data="lang_en"),
                InlineKeyboardButton(text=PT["lang_pt"], callback_data="lang_pt"),
            ]
        ]
    )