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
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")
if not RENDER_URL:
    raise ValueError("RENDER_EXTERNAL_URL not set in environment")

bot = Bot(TOKEN)
app = Flask(__name__)

# ---------- پاسخ کوتاه و حقوقی ----------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    reply = f"سلام {update.effective_user.first_name} عزیز!\n"
    reply += "این ربات توسط نسترن بنی‌طبا ساخته شده است و پاسخگوی سؤالات حقوقی شماست ⚖️\n\n"

    # نمونه فیلتر سؤالات حقوقی
    keywords = ["قرارداد", "وکالت", "طلاق", "مهریه", "اجاره"]
    if any(word in text for word in keywords):
        reply += ("پاسخ کوتاه: ⚖️\nبرای توضیح کامل و مشاوره تخصصی به سایت محضرباشی مراجعه کنید:\n"
                  "https://mahzarbashi.com")
    else:
        reply += "متأسفم، من فقط سؤالات حقوقی را پاسخ می‌دهم. برای اطلاعات بیشتر به سایت محضرباشی مراجعه کنید."

    # دکمه صوتی
    keyboard = [[InlineKeyboardButton("🎧 گوش دادن صوتی", callback_data=f"voice:{reply}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(reply, reply_markup=reply_markup)

# ---------- هندلر دکمه صوتی ----------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("voice:"):
        text = query.data.replace("voice:", "")
        tts = gTTS(text=text, lang="fa")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            with open(tmp_file.name, "rb") as audio:
                await bot.send_audio(chat_id=query.message.chat_id, audio=audio, title="پاسخ صوتی 🎧")
        await query.edit_message_text("✅ فایل صوتی برات فرستادم 🎵")

# ---------- اپلیکیشن PTB ----------
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
application.add_handler(CallbackQueryHandler(button_handler))

# ---------- مسیر وبهوک Flask ----------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook_route():
    update = Update.de_json(request.get_json(force=True), bot)
    asyncio.get_event_loop().create_task(application.update_queue.put(update))
    return "OK", 200

@app.route("/")
def index():
    return "🤖 Mahzarbashi Bot running", 200

# ---------- اجرای Flask در Thread ----------
def run_flask():
    app.run(host="0.0.0.0", port=PORT)

# ---------- Main async ----------
async def main():
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    await application.initialize()
    await application.start()

    webhook_url = f"{RENDER_URL}/{TOKEN}"
    await bot.set_webhook(webhook_url)
    print("✅ Webhook set to:", webhook_url)

    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await application.stop()
        await application.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
