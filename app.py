from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from gtts import gTTS
from flask import Flask, request
import os
import threading

BOT_TOKEN = "8249435097:AAF8PSgEXDVYWYBIXn_q45bHKID_aYDAtqw"
WEBHOOK_PATH = "/webhook"
app = Flask(__name__)

FAQ = {
    "چگونه سند ملک بگیرم؟": "برای گرفتن سند ملک، باید مراحل A و B و C را طی کنید...",
    "هزینه ثبت قرارداد چقدر است؟": "هزینه ثبت قرارداد بستگی به نوع قرارداد دارد، معمولا بین X تا Y تومان است.",
    "نحوه انتقال مالکیت خودرو؟": "برای انتقال مالکیت خودرو، ابتدا مدارک شناسایی و سند خودرو را آماده کنید و به دفترخانه مراجعه نمایید."
}

# ========================
# فرمان /start
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
# پردازش پیام‌ها
# ========================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    answer = FAQ.get(text)

    if answer:
        await update.message.reply_text(answer)
        tts = gTTS(answer, lang="fa")
        audio_file = "answer.mp3"
        tts.save(audio_file)
        await update.message.reply_voice(voice=open(audio_file, "rb"))
        os.remove(audio_file)
    else:
        msg = (
            "سوال شما نیاز به بررسی تخصصی دارد.\n"
            "لطفاً به وبسایت محضرباشی مراجعه کنید و با وکلای ما در تماس باشید:\n"
            "https://www.mahzarbashi.ir"
        )
        await update.message.reply_text(msg)

# ========================
# ساخت Application
# ========================
application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ========================
# اجرا در Thread جداگانه برای Webhook
# ========================
def run_app():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_app).start()

# ========================
# مسیر وب‌هوک Flask
# ========================
@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.create_task(application.process_update(update))
    return "ok", 200

@app.route("/")
def index():
    return "Bot is running!", 200
