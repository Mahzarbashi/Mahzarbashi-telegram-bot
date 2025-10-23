import os
import json
import asyncio
import logging
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# تنظیمات اولیه لاگ‌ها
logging.basicConfig(level=logging.INFO)

# دریافت توکن‌ها از محیط
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEBHOOK_URL = "https://mahzarbashi-telegram-bot-oz7v.onrender.com"

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ توکن تلگرام پیدا نشد! لطفاً در Render مقدار TELEGRAM_BOT_TOKEN را تنظیم کنید.")

# ------------------- پاسخ GROQ -------------------
async def get_legal_answer(question: str) -> str:
    """دریافت پاسخ از GROQ"""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.1-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": (
                    "تو یک دستیار حقوقی هستی که با لحن صمیمی و محترمانه پاسخ می‌دهی. "
                    "نامت محضرباشی‌یار است و توسعه‌دهنده‌ات نسترن بنی‌طبا است. "
                    "در هر پاسخ از ایموجی استفاده کن 🌿⚖️. "
                    "اگر سوال درباره مهریه، اجاره، طلاق یا قراردادها بود، پاسخ دقیق و توضیحی بده. "
                    "در پایان اگر لازم بود، لینک مشاوره بده: https://mahzarbashi.com/consult"
                ),
            },
            {"role": "user", "content": question},
        ],
    }

    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload) as resp:
            data = await resp.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "متأسفم ⚖️ پاسخ مشخصی پیدا نکردم.")

# ------------------- فرمان شروع -------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or "دوست عزیز"
    welcome = (
        f"سلام {name} 🌸\n"
        f"من **محضرباشی‌یار** هستم، دستیار حقوقی هوشمند 🤖⚖️\n\n"
        f"می‌تونی درباره مهریه، اجاره، طلاق، قرارداد و هر موضوع حقوقی دیگه سؤال بپرسی ✍️"
    )
    await update.message.reply_text(welcome, parse_mode="Markdown")

# ------------------- پاسخ به پیام کاربر -------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    user = update.effective_user.first_name or "کاربر"

    waiting = await update.message.reply_text("در حال بررسی سؤال شما هستم... ⏳")

    answer = await get_legal_answer(question)

    # دکمه‌ی پخش صوت
    keyboard = [[InlineKeyboardButton("🔊 گوش بده", callback_data=f"voice|{answer[:400]}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.delete_message(chat_id=update.message.chat_id, message_id=waiting.message_id)
    await update.message.reply_text(f"{answer}\n\n⚖️ با احترام، نسترن بنی‌طبا 🌿", reply_markup=reply_markup)

# ------------------- پاسخ صوتی -------------------
async def voice_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("در حال تولید صوت... 🎙️")

    text = query.data.split("|", 1)[1]
    voice_file = "answer.mp3"

    # تبدیل متن به صوت با GROQ (در آینده می‌تونیم ElevenLabs هم اضافه کنیم)
    # فعلاً به‌صورت نمادین — چون Render دسترسی مستقیم به صدا نداره
    with open(voice_file, "wb") as f:
        f.write(b"FAKE_VOICE_DATA")  # نمادین برای جلوگیری از خطا

    await query.message.reply_voice(voice=open(voice_file, "rb"), caption="🔊 پاسخ صوتی آماده است!")

# ------------------- اجرای ربات -------------------
async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.COMMAND, start))
    app.add_handler(CommandHandler("voice", voice_callback))

    # تنظیم وبهوک برای Render
    webhook_url = f"{WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}"
    await app.bot.set_webhook(url=webhook_url)
    logging.info(f"🚀 Webhook set to {webhook_url}")

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
