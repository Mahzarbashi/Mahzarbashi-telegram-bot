# main.py — Webhook-safe for Render
import os
import threading
import asyncio
import tempfile
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from gtts import gTTS

# ---------- تنظیمات ----------
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN not set in environment")

PORT = int(os.environ.get("PORT", 8443))
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")  # e.g. https://your-app.onrender.com
if not RENDER_URL:
    raise ValueError("RENDER_EXTERNAL_URL not set in environment")

bot = Bot(TOKEN)
app = Flask(__name__)

# ---------- پاسخ کوتاه مثال ----------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    reply = "این ربات توسط نسترن بنی‌طبا ساخته شده است.\nمن به سؤالات حقوقی پاسخ می‌دهم. مثال: مهریه، طلاق، قرارداد."
    await update.message.reply_text(reply)
    # صوتی (اختیاری)
    tts = gTTS(text=reply, lang="fa")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        tts.save(f.name)
        with open(f.name, "rb") as audio:
            await update.message.reply_voice(voice=audio)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("درخواست صوت ارسال شد.")

# ---------- ساخت اپلیکیشن PTB ----------
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
application.add_handler(CallbackQueryHandler(button_handler))

# ---------- مسیر وبهوک (Flask) ----------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook_route():
    # دریافت json و تبدیل به Update
    update = Update.de_json(request.get_json(force=True), bot)
    # قرار دادن در صف اپلیکیشن برای پردازش (async safe)
    asyncio.get_event_loop().create_task(application.update_queue.put(update))
    return "OK", 200

@app.route("/")
def index():
    return "🤖 Mahzarbashi Bot running", 200

# ---------- اجرای Flask در thread جدا ----------
def run_flask():
    # Note: use host 0.0.0.0 so Render can see it
    app.run(host="0.0.0.0", port=PORT)

# ---------- main async: راه‌اندازی PTB و ست کردن وبهوک ----------
async def main():
    # اجرا کردن Flask در یک ترد داِمون
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # initialize and start PTB application
    await application.initialize()
    await application.start()

    # ست کردن وبهوک به آدرس Render
    webhook_url = f"{RENDER_URL}/{TOKEN}"
    await bot.set_webhook(webhook_url)
    print("✅ Webhook set to:", webhook_url)

    # PTB خودش باید آماده دریافت update_queue باشه؛ نگه داشتن برنامه
    # اینجا فقط منتظر می‌مانیم که برنامه فعال بماند.
    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await application.stop()
        await application.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
