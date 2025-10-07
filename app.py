from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters
from gtts import gTTS
import os

# ========================
# تنظیمات ربات
# ========================
BOT_TOKEN = "8249435097:AAF8PSgEXDVYWYBIXn_q45bHKID_aYDAtqw"
bot = Bot(token=BOT_TOKEN)
bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)

# سوالات رایج و پاسخ‌ها
FAQ = {
    "چگونه سند ملک بگیرم؟": "برای گرفتن سند ملک، باید مراحل A و B و C را طی کنید...",
    "هزینه ثبت قرارداد چقدر است؟": "هزینه ثبت قرارداد بستگی به نوع قرارداد دارد، معمولا بین X تا Y تومان است.",
    "نحوه انتقال مالکیت خودرو؟": "برای انتقال مالکیت خودرو، ابتدا مدارک شناسایی و سند خودرو را آماده کنید و به دفترخانه مراجعه نمایید."
}

# ========================
# دستورات ربات
# ========================
def start(update: Update, context):
    welcome_text = (
        "سلام! من دستیار حقوقی محضرباشی هستم.\n"
        "می‌توانم به سوالات رایج حقوقی پاسخ بدهم.\n"
        "اگر سوال شما تخصصی باشد، به وبسایت محضرباشی هدایت خواهید شد.\n"
        "سوالت رو بپرسید:"
    )
    update.message.reply_text(welcome_text)

def handle_message(update: Update, context):
    text = update.message.text.strip()
    answer = FAQ.get(text)

    if answer:
        # پاسخ متنی
        update.message.reply_text(answer)
        # پاسخ صوتی
        tts = gTTS(answer, lang="fa")
        audio_file = "answer.mp3"
        tts.save(audio_file)
        update.message.reply_voice(voice=open(audio_file, "rb"))
        os.remove(audio_file)
    else:
        # سوال تخصصی → هدایت به سایت
        msg = (
            "سوال شما نیاز به بررسی تخصصی دارد.\n"
            "لطفاً به وبسایت محضرباشی مراجعه کنید و با وکلای ما در تماس باشید:\n"
            "https://www.mahzarbashi.ir"
        )
        update.message.reply_text(msg)

# ========================
# Dispatcher برای وب هوک
# ========================
dispatcher = Dispatcher(bot, None, workers=0)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ========================
# مسیر وب هوک
# ========================
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok", 200

# مسیر پیش‌فرض برای تست
@app.route("/")
def index():
    return "Bot is running!", 200

# ========================
# اجرای Flask
# ========================
if __name__ == "__main__":
    # روی Render، پورت از محیط گرفته می‌شود
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
