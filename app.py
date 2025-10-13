import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from gtts import gTTS
from io import BytesIO

# دریافت توکن‌ها از Environment Variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  # اگر نیاز به GPT داری

if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN پیدا نشد. لطفاً Environment Variables را تنظیم کنید.")

# دستور start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "سلام! من ربات محضرباشی هستم 🤖\n"
        "می‌تونی از من سوالات حقوقی بپرسی.\n\n"
        "برای اطلاعات بیشتر دستور /about را بزن."
    )
    await update.message.reply_text(text)

# دستور about (نمایش سازنده و سایت)
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "ربات مشاور حقوقی سایت محضرباشی\n"
        "وبسایت: www.mahzarbashi.ir\n"
        "این ربات توسط نسترن بنی طبا ساخته شده است."
    )
    await update.message.reply_text(text)

# پاسخ صوتی
async def voice_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    # اینجا می‌تونی API GPT وصل کنی و پاسخ تولید کنی
    response_text = f"پاسخ شما: {user_text}"  # نمونه ساده

    # تبدیل متن به صدا
    tts = gTTS(response_text, lang='fa')
    audio = BytesIO()
    tts.write_to_fp(audio)
    audio.seek(0)
    
    await update.message.reply_text(response_text)  # متن
    await update.message.reply_voice(voice=audio)  # صوت

# ساخت اپلیکیشن
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# هندلرها
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("about", about))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, voice_response))

# اجرای ربات
if __name__ == "__main__":
    print("🚀 Mahzarbashi Bot is running...")
    app.run_polling()
