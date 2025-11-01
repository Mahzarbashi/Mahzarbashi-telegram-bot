import os
import asyncio
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from gtts import gTTS

TOKEN = os.environ.get("BOT_TOKEN")

# ایجاد اپلیکیشن تلگرام
application = Application.builder().token(TOKEN).build()

# ایجاد اپلیکیشن FastAPI
app = FastAPI()

# فرمان /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام 👋 من ربات محضرباشی‌ام!\nسؤالت رو بنویس تا راهنماییت کنم.")

# پاسخ به پیام‌های متنی
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    response_text = f"پاسخ خودکار: درباره‌ی «{text}» به‌زودی توضیح داده می‌شود."

    # پاسخ متنی
    await update.message.reply_text(response_text)

    # پاسخ صوتی با gTTS
    tts = gTTS(response_text, lang="fa")
    tts.save("reply.mp3")
    await update.message.reply_voice(voice=open("reply.mp3", "rb"))

# افزودن هندلرها
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

# مسیر webhook
@app.post(f"/{TOKEN}")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}

# مسیر تست (صفحه‌ی اصلی)
@app.get("/")
def home():
    return {"status": "Bot is running ✅"}

# اجرای ربات با Webhook
async def main():
    await application.initialize()
    await application.start()
    await application.bot.set_webhook(
        url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    )
    print("Webhook set and bot started ✅")

    # منتظر ماندن برای همیشه
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
