import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")  # توکن ربات از محیط Render
app = Flask(__name__)

# ساخت اپلیکیشن تلگرام
application = Application.builder().token(TOKEN).build()


# دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام 👋 خوش اومدی به ربات محضرباشی!")


# پاسخ به پیام‌های متنی
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"پیام شما دریافت شد: {update.message.text}")


# هندلرها
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))


# وبهوک روت
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok", 200


@app.route("/")
def index():
    return "Mahzarbashi Telegram Bot is running!", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    application.run_polling()  # فقط برای لوکال
    app.run(host="0.0.0.0", port=port)
