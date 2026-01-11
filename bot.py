import os
import threading
import json
from datetime import datetime, timedelta

import telebot
from telebot import types
from flask import Flask

print("DEBUG: бот запускается")

# ====== Настройки ======

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("Не задана переменная окружения BOT_TOKEN")
print("DEBUG: BOT_TOKEN найден")

# срок тестовой подписки
SUBSCRIPTION_DAYS = 7
SUBS_FILE = "subscriptions.json"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ====== Работа с подписками ======

def load_subscriptions():
    if not os.path.exists(SUBS_FILE):
        return {}
    try:
        with open(SUBS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {}

    result = {}
    for user_id_str, expires_str in data.items():
        try:
            user_id = int(user_id_str)
            expires = datetime.fromisoformat(expires_str)
            result[user_id] = expires
        except Exception:
            continue
    return result


def save_subscriptions(subs):
    data = {str(uid): dt.isoformat() for uid, dt in subs.items()}
    with open(SUBS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


subscriptions = load_subscriptions()


def is_subscribed(user_id: int) -> bool:
    expires = subscriptions.get(user_id)
    if not expires:
        return False
    return expires > datetime.utcnow()


# ====== Хендлеры бота ======

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(
        types.KeyboardButton("ℹ️ О боте"),
        types.KeyboardButton("💼 Услуги"),
    )
    markup.row(
        types.KeyboardButton("💳 Подписка"),
        types.KeyboardButton("📞 Контакты"),
    )

    text = (
        "Привет 👋\n"
        "Я пример Telegram-бота для бизнеса.\n\n"
        "Для доступа к разделу «💼 Услуги» нужна подписка.\n\n"
        "Команды:\n"
        "/buy – оформить ТЕСТОВУЮ подписку (без оплаты)\n"
        "/status – статус подписки"
    )

    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == "ℹ️ О боте")
def about(message):
    bot.send_message(
        message.chat.id,
        "Этот бот создан как пример.\n"
        "Можно сделать такого же под ваш бизнес."
    )


@bot.message_handler(func=lambda m: m.text == "📞 Контакты")
def contacts(message):
    bot.send_message(message.chat.id, "Связь: @treechet")


@bot.message_handler(func=lambda m: m.text == "💼 Услуги")
def services(message):
    user_id = message.from_user.id
    if not is_subscribed(user_id):
        bot.send_message(
            message.chat.id,
            "Раздел «💼 Услуги» доступен только по активной подписке.\n\n"
            "Оформить тестовую подписку: /buy или кнопка «💳 Подписка».\n"
            "Проверить статус: /status"
        )
        return

    bot.send_message(
        message.chat.id,
        "🔹 Telegram-боты под ключ\n"
        "🔹 Подписка и оплаты\n"
        "🔹 Автоматизация бизнеса"
    )


# ====== Тестовая подписка (без оплаты) ======

@bot.message_handler(commands=['buy'])
@bot.message_handler(func=lambda m: m.text == "💳 Подписка")
def buy(message):
    """ТЕСТОВАЯ подписка: активируем без денег."""
    user_id = message.from_user.id
    expires = datetime.utcnow() + timedelta(days=SUBSCRIPTION_DAYS)
    subscriptions[user_id] = expires
    save_subscriptions(subscriptions)

    bot.send_message(
        message.chat.id,
        "✅ Тестовая подписка активирована!\n"
        f"Действует до {expires.strftime('%d.%m.%Y %H:%M UTC')}.\n\n"
        "В реальной версии здесь будет оплата через Telegram Payments / YooKassa."
    )


@bot.message_handler(commands=['status'])
def status(message):
    """Показать статус подписки."""
    user_id = message.from_user.id
    expires = subscriptions.get(user_id)
    if not expires or expires <= datetime.utcnow():
        bot.send_message(
            message.chat.id,
            "У вас НЕТ активной подписки.\n"
            "Для теста можете активировать её командой /buy "
            "или кнопкой «💳 Подписка»."
        )
    else:
        bot.send_message(
            message.chat.id,
            "Подписка активна до "
            f"{expires.strftime('%d.%m.%Y %H:%M UTC')}."
        )


# ====== Запуск бота и Flask-сервера (для Render) ======

def run_bot():
    print("DEBUG: запускаем infinity_polling")
    bot.infinity_polling(skip_pending=True)
    print("DEBUG: infinity_polling завершился (такого быть не должно)")


@app.route("/")
def index():
    return "Bot is running"


if __name__ == "__main__":
    print("DEBUG: в блоке __main__")
    t = threading.Thread(target=run_bot, daemon=True)
    t.start()

    port_env = os.environ.get("PORT")
    print(f"DEBUG: значение PORT из окружения: {port_env}")
    port = int(port_env or 5000)
    print(f"DEBUG: запускаем Flask на порту {port}")
    app.run(host="0.0.0.0", port=port, use_reloader=False)
