import os
import logging
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import openai
from flask import Flask, request

# ==============================
# تنظیمات کلیدها
# ==============================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")  # مثال: 8249435097:AAEqSw...
APP_URL = os.environ.get("APP_URL")  # مثال: https://mahzarbashi-telegram-bot-v2-1.onrender.com
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  # مثال: sk-...

openai.api_key = OPENAI_API_KEY

# ==============================
# فعال کردن لاگ برای دیباگ
# ==============================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ==============================
# Flask app برای Webhook
# ==============================
app = Flask(__name__)
bot = Bot(token=TELEGRAM_TOKEN)

# ==============================
# پیام خوش‌آمدگویی /start
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "سلام! 👋\n"
        "من دستیار حقوقی محضرباشی هستم.\n"
        "این ربات توسط نسترن بنی طبا ساخته شده و می‌تونه به سوالات حقوقی شما پاسخ بده.\n\n"
        "📌 راهنمای استفاده:\n"
        "1️⃣ سوال حقوقی خود را تایپ کنید.\n"
        "2️⃣ اگر سوال ساده باشد، پاسخ کامل دریافت می‌کنید.\n"
        "3️⃣ اگر موضوع پیچیده باشد، برای مشاوره دقیق‌تر به وکلای محضرباشی ارجاع داده می‌شوید.\n\n"
        "برای شروع، لطفاً سوال خود را وارد کنید."
    )
    await update.message.reply_text(welcome_text)

# ==============================
# پردازش پیام کاربران
# ==============================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = update.message.text

    # بررسی پیچیدگی سوال (معیار ساده)
    if len(user_question.split()) > 40:
        await update.message.reply_text(
            "این موضوع کمی پیچیده است. لطفاً برای مشاوره دقیق‌تر به وکلای محضرباشی مراجعه کنید."
        )
        return

    # تولید پاسخ با GPT
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "تو یک دستیار حقوقی حرفه‌ای هستی. پاسخ‌ها دقیق، قابل فهم و کامل بده."},
                {"role": "user", "content": user_question}
            ],
            max_tokens=600
        )
        answer = response.choices[0].message.content
        await update.message.reply_text(answer)
    except Exception as e:
        await update.message.reply_text("متاسفانه مشکلی پیش آمد، دوباره تلاش کنید.")
        logging.error(e)

# ==============================
# ساخت اپلیکیشن تلگرام
# ==============================
application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ==============================
# Webhook با Flask
# ==============================
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.create_task(application.update_queue.put(update))
    return "OK"

# ==============================
# اجرای Webhook روی Render
# ==============================
if __name__ == "__main__":
    # تنظیم Webhook روی Render
    bot.set_webhook(f"{APP_URL}/{TELEGRAM_TOKEN}")
    print("Bot is running with Webhook...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
