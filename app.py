import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# گرفتن توکن از متغیر محیطی Render (توصیه امنیتی)
TOKEN = os.environ.get("BOT_TOKEN", "اینجا_توکن_ربات_رو_قرار_بده")

# ساخت Flask app
app = Flask(__name__)

# ساخت اپلیکیشن تلگرام
application = Application.builder().token(TOKEN).build()

# ---- هندلرها ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام 👋 خوش اومدی به ربات محضرباشی.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("من می‌تونم بهت کمک کنم. فقط پیام بده 🌹")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"گفتی: {update.message.text}")

# اضافه کردن هندلرها
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# ---- وبهوک ----
@app.route("/webhook", methods=["POST"])
async def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
    except Exception as e:
        print("Error in webhook:", e)
    return "ok", 200

# تست صفحه اصلی Render
@app.route("/")
def home():
    return "Mahzarbashi Bot is running ✅"

# برای اجرای لوکال
if __name__ == "__main__":
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        webhook_url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook"
    )
