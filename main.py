import os
import asyncio
from fastapi import FastAPI, Request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler, MessageHandler, filters
from gtts import gTTS
import tempfile
import nest_asyncio
import uvicorn

nest_asyncio.apply()

TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("❌ توکن تلگرام پیدا نشد! لطفاً TELEGRAM_TOKEN را در Render تنظیم کن.")

WEBHOOK_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"

bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()

# ---- پاسخ به پیام‌ها ----
async def handle_message(update: Update, context):
    text = update.message.text.lower().strip()

    if any(word in text for word in ["قانون", "طلاق", "حقوق", "قرارداد", "مهریه", "شکایت"]):
        reply = (
            f"👋 سلام {update.effective_user.first_name}!\n"
            "من دستیار هوشمند حقوقی محضرباشی هستم.\n"
            f"سؤال شما:\n{text}\n\n"
            "📚 پاسخ: برای اطلاعات بیشتر به سایت محضرباشی مراجعه کن 🌐 mahzarbashi.ir"
        )
    else:
        reply = (
            f"سلام {update.effective_user.first_name} 🌸\n"
            "من فقط به پرسش‌های حقوقی پاسخ می‌دم.\n"
            "برای سایر موضوعات لطفاً به سایت محضرباشی مراجعه کن 💼"
        )

    keyboard = [[InlineKeyboardButton("🎧 پاسخ صوتی", callback_data=f"voice:{reply}")]]
    await update.message.reply_text(reply, reply_markup=InlineKeyboardMarkup(keyboard))

# ---- پاسخ صوتی ----
async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("voice:"):
        text = query.data.replace("voice:", "")
        tts = gTTS(text=text, lang='fa')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            await bot.send_audio(chat_id=query.message.chat.id, audio=open(tmp_file.name, 'rb'))
        await query.edit_message_text("✅ فایل صوتی برات فرستادم 🎧")

# ---- هندلرها ----
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
application.add_handler(CallbackQueryHandler(button_handler))

# ---- FastAPI ----
app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await application.initialize()
    await bot.set_webhook(url=WEBHOOK_URL)
    print(f"✅ Webhook set: {WEBHOOK_URL}")

@app.post(f"/{TOKEN}")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    await application.process_update(update)
    return {"ok": True}

@app.get("/")
async def home():
    return {"message": "🤖 Mahzarbashi Assistant Bot is running successfully!"}

# ---- اجرای Uvicorn در Render ----
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
