import os
import logging
from gtts import gTTS
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

# فعال کردن لاگ‌ها
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# توکن ربات
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("❌ توکن تلگرام پیدا نشد! لطفاً TELEGRAM_TOKEN را در Render تنظیم کنید.")

# مسیر ذخیره فایل‌های صوتی
VOICE_DIR = "voices"
os.makedirs(VOICE_DIR, exist_ok=True)

# --- دستور شروع ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "سلام 👋\n"
        "به ربات حقوقی محضرباشی خوش اومدی ⚖️\n"
        "هر سوال حقوقی داری بپرس تا هم با صدا و هم متن راهنماییت کنم ✨"
    )
    await update.message.reply_text(text)
    await send_voice(update, text)

# --- تولید و ارسال صوت ---
async def send_voice(update: Update, text: str):
    tts = gTTS(text=text, lang="fa")
    filename = f"{VOICE_DIR}/reply.mp3"
    tts.save(filename)
    with open(filename, "rb") as voice_file:
        await update.message.reply_voice(voice=voice_file)

# --- پاسخ به پیام‌ها ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip().lower()

    if "طلاق" in user_text:
        answer = "برای طلاق باید دادخواست در دفتر خدمات قضایی ثبت بشه 👩‍⚖️"
    elif "مهریه" in user_text:
        answer = "زن می‌تونه برای مهریه از طریق اجرای ثبت یا دادگاه خانواده اقدام کنه 💰"
    elif "حضانت" in user_text:
        answer = "حضانت تا ۷ سالگی با مادره و بعد از اون با نظر دادگاه تعیین میشه 👶"
    elif "نفقه" in user_text:
        answer = "نفقه شامل هزینه‌های متعارف زندگی زوجه است و مرد موظفه پرداخت کنه 💵"
    else:
        answer = "سوالت حقوقی‌تر بپرس تا دقیق‌تر راهنماییت کنم ⚖️"

    await update.message.reply_text(answer)
    await send_voice(update, answer)

# --- اجرای اصلی ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
