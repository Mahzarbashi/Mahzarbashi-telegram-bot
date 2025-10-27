import os
import nest_asyncio
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from gtts import gTTS
import tempfile
import uvicorn
import asyncio

nest_asyncio.apply()  # حل مشکل loop در Render

TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("توکن تلگرام پیدا نشد!")

bot = Bot(token=TOKEN)
app = FastAPI()

# پاسخ حقوقی با دکمه صوتی
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_text = (
        f"سلام {update.effective_user.first_name} عزیز! 👋\n"
        "این ربات توسط نسترن بنی طبا ساخته شده است.\n"
        "من پاسخگوی سؤالات حقوقی هستم.\n"
        "برای جزئیات بیشتر به وبسایت محضرباشی مراجعه کنید."
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

# ساخت اپلیکیشن تلگرام
application = Application.builder().token(TOKEN).build()
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
application.add_handler(CallbackQueryHandler(button_handler))

# وبهوک FastAPI
@app.post(f"/{TOKEN}")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    asyncio.create_task(application.update_queue.put(update))
    return {"ok": True}

@app.get("/")
def root():
    return {"status": "🤖 ربات محضرباشی فعال است!"}

if __name__ == "__main__":
    hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    if not hostname:
        raise ValueError("RENDER_EXTERNAL_HOSTNAME پیدا نشد!")

    webhook_url = f"https://{hostname}/{TOKEN}"
    asyncio.run(bot.set_webhook(webhook_url))
    print(f"✅ Webhook set to: {webhook_url}")

    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
