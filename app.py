import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# گرفتن توکن از Environment Variable
TOKEN = os.environ.get("BOT_TOKEN")

# ساخت اپ Flask
app = Flask(__name__)

# ساخت اپلیکیشن تلگرام
application = Application.builder().token(TOKEN).build()

# دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام 👋 خوش آمدید به ربات محضرباشی.")

# دستور /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("دستورات موجود:\n/start - شروع\n/help - راهنما")

# اضافه کردن هندلرها
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))

# وبهوک برای دریافت پیام‌ها
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put(update)
    return "OK"

# صفحه تست
@app.route("/", methods=["GET"])
def home():
    return "Bot is alive ✅"

if __name__ == "__main__":
    # برای اجرا در حالت لوکال
    application.run_polling()
