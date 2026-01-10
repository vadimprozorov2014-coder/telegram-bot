import telebot
from telebot import types

TOKEN = "8577195980:AAFaS5cJCOjSUBFcOS7SnEFcz4gmGf908Jc"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton("ℹ️ О боте"),
        types.KeyboardButton("💼 Услуги"),
        types.KeyboardButton("📞 Контакты")
    )

    bot.send_message(
        message.chat.id,
        "Привет 👋\nЯ пример Telegram-бота для бизнеса.",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "ℹ️ О боте")
def about(message):
    bot.send_message(
        message.chat.id,
        "Этот бот создан как пример.\n"
        "Можно сделать такого же под ваш бизнес."
    )

@bot.message_handler(func=lambda message: message.text == "💼 Услуги")
def services(message):
    bot.send_message(
        message.chat.id,
        "🔹 Telegram-боты под ключ\n"
        "🔹 Подписка и оплаты\n"
        "🔹 Автоматизация бизнеса"
    )

@bot.message_handler(func=lambda message: message.text == "📞 Контакты")
def contacts(message):
    bot.send_message(
        message.chat.id,
        "Связь: @treechet"
    )

bot.infinity_polling()
