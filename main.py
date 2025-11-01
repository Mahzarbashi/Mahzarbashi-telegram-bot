import os
import asyncio
from fastapi import FastAPI, Request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters, CallbackContext
from gtts import gTTS
import tempfile
import nest_asyncio
from contextlib import asynccontextmanager

nest_asyncio.apply()

TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("❌ توکن تلگرام پیدا نشد! لطفاً متغیر TELEGRAM_TOKEN را در Render تنظیم کن.")

WEBHOOK_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"

bot = Bot(token=TOKEN)
application = Application.builder().bot(bot).build()

# پاسخ به پیام‌ها
async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text.strip().lower()

    if any(word in text for word in ["قانون", "حقوق", "وکالت", "طلاق", "مهریه", "قرارداد"]):
        reply_text = (
            f"👋 سلام {update.effective_user.first_name}!\n"
            "من دستیار هوشمند حقوقی محضرباشی هستم.\n"
            "سؤال شما:\n"
            f"{update.message.text}\n\n"
            "📚 پاسخ: برای جزئیات بیشتر لطفاً به سایت محضرباشی مراجعه کنید.\n"
            "🌐 mahzarbashi.ir"
        )
    else:
        reply_text = (
            f"سلام {update.effective_user.first_name} 🌸\n"
            "من فقط به پرسش‌های حقوقی پاسخ می‌دم.\n"
            "برای سایر موضوعات لطفاً به سایت محضرباشی مراجعه کنید 💼"
        )

    keyboard = [[InlineKeyboardButton("🎧 گوش دادن به پاسخ صوتی", callback_data=f"voice:{reply_text}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(reply_text, reply_markup=reply_markup)

# پاسخ صوتی
async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("voice:"):
        text = query.data.replace("voice:", "")
        tts = gTTS(text=text, lang='fa')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            await bot.send_audio(chat_id=query.message.chat_id, audio=open(tmp_file.name, 'rb'), title="پاسخ صوتی 🎵")
        await query.edit_message_text("✅ فایل صوتی برات فرستادم 🎧")

# هندلرها
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
application.add_handler(CallbackQueryHandler(button_handler))

# FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    await application.initialize()
    await application.start()
    await bot.set_webhook(WEBHOOK_URL)
    print("✅ Webhook set to:", WEBHOOK_URL)
    yield
    await application.stop()
    await application.shutdown()

app = FastAPI(lifespan=lifespan)

@app.post(f"/{TOKEN}")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    asyncio.create_task(application.process_update(update))
    return {"ok": True}

@app.get("/")
async def home():
    return {"message": "🤖 Mahzarbashi Telegram Bot is alive and working perfectly!"}
