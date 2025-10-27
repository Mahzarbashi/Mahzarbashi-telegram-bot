import logging
import nest_asyncio
import asyncio
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8249435097:AAEqSwTL8Ah8Kfyzo9Z_iQE97OVUViXtOmY"
WEBHOOK_URL = f"https://mahzarbashi-telegram-bot-1-usa9.onrender.com/{TOKEN}"

# فعال کردن لاگ‌ها برای اشکال‌یابی
logging.basicConfig(level=logging.INFO)

# اصلاح حلقه event برای render
nest_asyncio.apply()

# FastAPI app
app = FastAPI()

# ایجاد bot و application
bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()

# دستور start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! 🤖 ربات محضرباشی آماده است ✅")

# هندل پیام‌های عادی
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f"شما گفتید: {text}")

# افزودن هندلرها
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# راه‌اندازی وبهوک
@app.on_event("startup")
async def startup():
    await bot.delete_webhook()
    await bot.set_webhook(url=WEBHOOK_URL)
    logging.info(f"✅ Webhook set to: {WEBHOOK_URL}")

# مسیر اصلی برای بررسی سلامت
@app.get("/")
async def home():
    return {"status": "Bot is running fine!"}

# مسیر وبهوک برای دریافت آپدیت‌ها از تلگرام
@app.post(f"/{TOKEN}")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    await application.initialize()
    await application.process_update(update)
    return {"ok": True}

# اجرای ربات در Render
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
