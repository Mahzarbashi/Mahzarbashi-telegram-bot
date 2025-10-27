import os
import nest_asyncio
import asyncio
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from gtts import gTTS
import tempfile

nest_asyncio.apply()  # حل مشکل event loop در Flask

TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("❌ توکن تلگرام پیدا نشد!")

bot = Bot(token=TOKEN)
app = Flask(__name__)

# پاسخ متنی و صوتی
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_text = (
        f"سلام {update.effective_user.first_name} عزیز! 👋\n"
        "این ربات توسط نسترن بنی طبا ساخته شده است.\n"
        "من پاسخگوی سؤالات حقوقی هستم.\n"
        "برای جزئیات بیشتر به وبسایت محضرباشی مراجعه کن."
    )
    keyboard = [[InlineKeyboardButton("🎧 گوش دادن صوتی", callback_data=f"voice:{reply_text}")]]
    await update.message.reply_text(reply_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("voice:"):
        text = query.data.replace("voice:", "")
        tts = gTTS(text=text, lang='fa')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            await bot.send_audio(chat_id=query.message.chat_id, audio=open(tmp_file.name, 'rb'), title="پاسخ صوتی 🎧")
        await query.edit_message_text("✅ فایل صوتی آماده شد!")

# ساخت اپلیکیشن
application = Application.builder().token(TOKEN).build()
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
application.add_handler(CallbackQueryHandler(button_handler))

# Flask route وبهوک
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    loop = asyncio.get_event_loop()
    loop.create_task(application.update_queue.put(update))
    return "OK"

@app.route("/")
def home():
    return "🤖 ربات محضرباشی فعال است!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    if not hostname:
        raise ValueError("❌ RENDER_EXTERNAL_HOSTNAME پیدا نشد!")

    webhook_url = f"https://{hostname}/{TOKEN}"
    asyncio.run(bot.set_webhook(webhook_url))
    print(f"✅ Webhook set to: {webhook_url}")

    app.run(host="0.0.0.0", port=port)
