from gtts import gTTS
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os

# ========================
# تنظیمات ربات
# ========================
BOT_TOKEN = "8310741380:AAHRrADEytsjTVZYtJle71e5twxFxqr556c"

# سوالات رایج و پاسخ‌ها
FAQ = {
    "چگونه سند ملک بگیرم؟": "برای گرفتن سند ملک، باید مراحل A و B و C را طی کنید...",
    "هزینه ثبت قرارداد چقدر است؟": "هزینه ثبت قرارداد بستگی به نوع قرارداد دارد، معمولا بین X تا Y تومان است.",
    "نحوه انتقال مالکیت خودرو؟": "برای انتقال مالکیت خودرو، ابتدا مدارک شناسایی و سند خودرو را آماده کنید و به دفترخانه مراجعه نمایید."
}

# ========================
# دستور /start
# ========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "سلام! من دستیار حقوقی محضرباشی هستم.\n"
        "می‌توانم به سوالات رایج حقوقی پاسخ بدهم.\n"
        "اگر سوال شما تخصصی باشد، به وبسایت محضرباشی هدایت خواهید شد.\n"
        "سوالت رو بپرسید:"
    )
    await update.message.reply_text(welcome_text)

# ========================
# پردازش پیام کاربر
# ========================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    answer = FAQ.get(text)

    if answer:
        # پاسخ متنی
        await update.message.reply_text(answer)
        # پاسخ صوتی
        tts = gTTS(answer, lang="fa")
        audio_file = "answer.mp3"
        tts.save(audio_file)
        await update.message.reply_voice(voice=open(audio_file, "rb"))
        os.remove(audio_file)
    else:
        # سوال تخصصی → هدایت به سایت
        msg = (
            "سوال شما نیاز به بررسی تخصصی دارد.\n"
            "لطفاً به وبسایت محضرباشی مراجعه کنید و با وکلای ما در تماس باشید:\n"
            "https://www.mahzarbashi.ir"
        )
        await update.message.reply_text(msg)

# ========================
# اجرای ربات
# ========================
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()
