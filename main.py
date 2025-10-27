import os
import tempfile
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from gtts import gTTS
import asyncio

# =======================
# ⚙️ تنظیمات ربات
# =======================
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("❌ توکن تلگرام پیدا نشد! لطفاً TELEGRAM_TOKEN را در Render تنظیم کنید.")

PORT = int(os.environ.get("PORT", 8443))
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")  # آدرس پروژه روی Render

bot = Bot(TOKEN)
app = Flask(__name__)

# =======================
# هندلر پیام‌ها
# =======================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()

    reply_text = f"سلام {update.effective_user.first_name} عزیز!\n"
    reply_text += "این ربات توسط نسترن بنی‌طبا ساخته شده و پاسخگوی سؤالات حقوقی شماست ⚖️\n\n"

    if any(word in text for word in ["قرارداد", "وکالت", "طلاق", "مهریه", "اجاره"]):
        reply_text += ("سؤالت حقوقی دریافت شد. پاسخ کوتاه: ⚖️\n"
                       "برای توضیح کامل و مشاوره تخصصی به سایت محضرباشی مراجعه کنید:\n"
                       "https://mahzarbashi.com")
    else:
        reply_text += "متأسفم، من فقط سؤالات حقوقی رو پاسخ میدم. برای اطلاعات بیشتر به سایت محضرباشی مراجعه کنید."

    keyboard = [[InlineKeyboardButton("🎧 گوش دادن صوتی", callback_data=f"voice:{reply_text}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(reply_text, reply_markup=reply_markup)

# =======================
# هندلر دکمه صوتی
# =======================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("voice:"):
        text = query.data.replace("voice:", "")
        tts = gTTS(text=text, lang="fa")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            await bot.send_audio(chat_id=query.message.chat_id, audio=open(tmp_file.name, "rb"), title="پاسخ صوتی 🎧")
        await query.edit_message_text("✅ فایل صوتی برات فرستادم 🎵")

# =======================
# ساخت Application
# =======================
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
application.add_handler(CallbackQueryHandler(button_handler))

# =======================
# Flask route برای Webhook
# =======================
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    asyncio.get_event_loop().create_task(application.update_queue.put(update))
    return "OK"

@app.route("/")
def home():
    return "🤖 Mahzarbashi Bot is running! 💫"

# =======================
# اجرای Webhook
# =======================
async def main():
    await application.initialize()
    await application.start()
    await bot.set_webhook(f"{RENDER_URL}/{TOKEN}")
    print(f"✅ Webhook set to: {RENDER_URL}/{TOKEN}")
    await application.updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"{RENDER_URL}/{TOKEN}"
    )
    await application.updater.idle()

if __name__ == "__main__":
    asyncio.run(main())
