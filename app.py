import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import Bot
from gtts import gTTS
from io import BytesIO
import openai
from flask import Flask, request, Response

# دریافت توکن‌ها و پورت
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PORT = int(os.environ.get("PORT", 10000))
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")  # URL اصلی Render

if not TELEGRAM_TOKEN or not OPENAI_API_KEY or not RENDER_EXTERNAL_URL:
    raise ValueError("❌ لطفاً TELEGRAM_TOKEN، OPENAI_API_KEY و RENDER_EXTERNAL_URL را تنظیم کنید.")

openai.api_key = OPENAI_API_KEY

# Flask app برای webhook
app = Flask(__name__)
bot = Bot(token=TELEGRAM_TOKEN)

# دستور start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "سلام! من ربات محضرباشی هستم 🤖\n"
        "می‌تونی از من سوالات حقوقی بپرسی.\n\n"
        "برای اطلاعات بیشتر دستور /about را بزن."
    )
    await update.message.reply_text(text)

# دستور about
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "ربات مشاور حقوقی سایت محضرباشی\n"
        "وبسایت: www.mahzarbashi.ir\n"
        "این ربات توسط نسترن بنی طبا ساخته شده است."
    )
    await update.message.reply_text(text)

# پاسخ GPT و صوتی
async def gpt_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    
    system_prompt = (
        "تو یک مشاور حقوقی هستی. فقط به سوالات حقوقی پاسخ بده. "
        "اگر سوال تخصصی است، کوتاه جواب بده و کاربر را به سایت محضرباشی هدایت کن. "
        "پاسخ‌ها دوستانه، واضح و ساده باشد."
    )

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7
        )
        response_text = completion.choices[0].message.content.strip()
    except Exception:
        response_text = (
            "این سوال خارج از حوزه حقوقی است یا در حال حاضر نمی‌توانم پاسخ بدهم. "
            "لطفاً سوال حقوقی بپرسید یا به وبسایت محضرباشی مراجعه کنید: www.mahzarbashi.ir"
        )

    # ارسال متن
    await update.message.reply_text(response_text)

    # ارسال صوت
    tts = gTTS(response_text, lang='fa')
    audio = BytesIO()
    tts.write_to_fp(audio)
    audio.seek(0)
    await update.message.reply_voice(voice=audio)

# ساخت اپلیکیشن Telegram
from telegram.ext import Application
application = Application.builder().token(TELEGRAM_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("about", about))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gpt_response))

# وبهوک Flask
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    import asyncio
    asyncio.run(application.process_update(update))
    return Response("ok", status=200)

# اجرای Webhook و ست کردن آن روی تلگرام
if __name__ == "__main__":
    webhook_url = f"{RENDER_EXTERNAL_URL}/{TELEGRAM_TOKEN}"
    bot.set_webhook(url=webhook_url)
    print(f"🚀 Webhook set to {webhook_url}")
    app.run(host="0.0.0.0", port=PORT)
