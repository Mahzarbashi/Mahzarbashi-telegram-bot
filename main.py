import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import nest_asyncio
import asyncio
from gtts import gTTS

# ---------------------- تنظیمات اولیه ----------------------
TOKEN = os.getenv("BOT_TOKEN", "8249435097:AAEqSwTL8Ah8Kfyzo9Z_iQE97OVUViXtOmY")
WEBHOOK_URL = f"https://mahzarbashi-telegram-bot-1-usa9.onrender.com/{TOKEN}"

app = FastAPI()
nest_asyncio.apply()

# ساخت آبجکت ربات
application = Application.builder().token(TOKEN).build()


# ---------------------- هندلر پیام ----------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if not text:
        return

    if "سلام" in text:
        reply = "سلام! من ربات محضرباشی هستم 🌸 چطور می‌تونم کمکتون کنم؟"
    elif "حقوق" in text or "طلاق" in text:
        reply = "برای دریافت مشاوره حقوقی می‌تونید به سایت محضرباشی مراجعه کنید:\nhttps://mahzarbashi.ir"
    else:
        reply = "پرسشت رو واضح‌تر بگو تا راهنماییت کنم 🌷"

    keyboard = [
        [
            InlineKeyboardButton("💬 سوالات حقوقی", callback_data="faq"),
            InlineKeyboardButton("🌐 سایت محضرباشی", url="https://mahzarbashi.ir"),
        ]
    ]

    await update.message.reply_text(reply, reply_markup=InlineKeyboardMarkup(keyboard))


# ---------------------- هندلر دکمه‌ها ----------------------
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "faq":
        await query.edit_message_text(
            "سوالات متداول:\n\n1️⃣ نحوه دریافت مشاوره حقوقی\n2️⃣ هزینه تنظیم قرارداد\n3️⃣ ارتباط با وکیل"
        )


# ---------------------- FastAPI بخش ----------------------
@app.post(f"/{TOKEN}")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return JSONResponse(content={"ok": True})


@app.get("/")
async def root():
    return {"status": "Mahzarbashi Telegram Bot is running ✅"}


# ---------------------- Startup Event ----------------------
@app.on_event("startup")
async def on_startup():
    await application.bot.set_webhook(url=WEBHOOK_URL)
    print(f"✅ Webhook set to: {WEBHOOK_URL}")


# ---------------------- اجرای برنامه ----------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
