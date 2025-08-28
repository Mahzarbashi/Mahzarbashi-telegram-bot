from flask import Flask, request
import telegram
import os

TOKEN = "توکن_جدید_تو"  # اینجا توکن جدید رو بذار
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

@app.route(f'/{TOKEN}', methods=['POST'])
def respond():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    message = update.message.text

    if message == "/start":
        bot.sendMessage(chat_id=chat_id, text="سلام! ربات محضرباشی آماده‌ست 🌿")
    else:
        bot.sendMessage(chat_id=chat_id, text="پیامت رسید ✅")

    return "ok"

@app.route('/')
def index():
    return "ربات محضرباشی فعال است ✅"

if __name__ == '__main__':
    app.run(threaded=True)
