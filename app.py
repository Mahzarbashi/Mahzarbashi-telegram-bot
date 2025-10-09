import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from openai import OpenAI

# 🔑 توکن جدید تلگرام (که از BotFather گرفتی)
TELEGRAM_BOT_TOKEN = "8249435097:AAGOIS7GfwBayCTSZGFahbMhYcZDFxzSGAg"

# 🔑 کلید OpenAI باید از Environment Variable خونده بشه
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# اتصال به OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# ساخت اپلیکیشن تلگرام
telegram_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# ساخت اپ Flask
app = Flask(__name__)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام 👋 من ربات محضرباشی هستم. هر سوالی داری بپرس!")

# هندل پیام‌ها
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    try:
        # درخواست به OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "تو یک مشاور حقوقی هوشمند هستی. سوالات ساده را پاسخ بده، اما اگر سوال تخصصی و مهم بود کاربر را به وبسایت محضرباشی (www.mahzarbashi.ir) هدایت کن."},
                {"role": "user", "content": user_message}
            ]
        )
        answer = response.choices[0].message.content
        await update.message.reply_text(answer)

    except Exception as e:
        await update.message.reply_text("مشکلی پیش آمد، لطفاً دوباره تلاش کن.")

# ثبت هندلرها
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Flask route برای وبهوک
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    telegram_app.update_queue.put_nowait(update)
    return "ok", 200

if __name__ == "__main__":
    telegram_app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        url_path="webhook",
        webhook_url=f"{os.environ.get('RENDER_EXTERNAL_URL')}/webhook"
    )
