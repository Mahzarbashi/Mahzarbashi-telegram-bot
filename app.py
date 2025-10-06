from flask import Flask, request
from telegram import Bot, Update
import os

app = Flask(__name__)

# توکن ربات
TOKEN = "8310741380:AAHRrADEytsjTVZYtJle71e5twxFxqr556c"
bot = Bot(token=TOKEN)

@app.route('/')
def index():
    return "Bot is running!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), bot)

        if update.message:
            chat_id = update.message.chat.id
            text = update.message.text

            if text == "/start":
                bot.send_message(chat_id=chat_id, text="سلام! خوش آمدید به ربات محضرباشی.")
            else:
                bot.send_message(chat_id=chat_id, text=f"پیام شما دریافت شد: {text}")

        return "ok", 200
    except Exception as e:
        print(f"Error: {e}")
        return "error", 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
