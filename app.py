# app.py
from flask import Flask, request
from telegram import Bot, Update

# =====================
# تنظیمات ربات
# =====================
BOT_TOKEN = "8249435097:AAF8PSgEXDVYWYBIXn_q45bHKID_aYDAtqw"
WEBHOOK_PATH = "/webhook"  # مسیر webhook
bot = Bot(BOT_TOKEN)

# =====================
# تعریف اپلیکیشن Flask
# =====================
app = Flask(__name__)

# مسیر Webhook
@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), bot)
        if update.message:  # پیام متنی دریافت شد
            chat_id = update.message.chat.id
            text = update.message.text

            # پاسخ ساده به پیام
            bot.send_message(chat_id=chat_id, text=f"پیام شما دریافت شد: {text}")

        return "OK", 200
    except Exception as e:
        print(f"Webhook Error: {e}")
        return "Error", 500

# صفحه اصلی برای تست سرویس
@app.route("/")
def index():
    return "ربات زنده است ✅", 200

# =====================
# اجرای ربات (برای اجرا روی Render)
# =====================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
