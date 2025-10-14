import os
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from gtts import gTTS
import openai
import aiohttp

# تنظیمات پایه
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL")

openai.api_key = OPENAI_API_KEY

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ساخت اپلیکیشن تلگرام
application = Application.builder().token(TELEGRAM_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 👋 من دستیار حقوقی محضرباشی هستم. هر سوالی درباره‌ی امور حقوقی داری بپرس."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    # بررسی اینکه سوال حقوقی هست یا نه
    keywords = ["مهریه", "طلاق", "سند", "شکایت", "دادگاه", "وکالت", "نفقه", "قرارداد", "اجاره"]
    if not any(k in user_text for k in keywords):
        await update.message.reply_text(
            "من فقط به سوالات حقوقی پاسخ می‌دهم ⚖️ لطفاً سؤال خود را در زمینه‌ی حقوق بپرس."
        )
        return

    try:
        # درخواست به GPT
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "شما یک مشاور حقوقی فارسی هستید. پاسخ‌ها را کوتاه، دقیق و قابل فهم بده."},
                {"role": "user", "content": user_text}
            ],
            max_tokens=350,
        )

        answer = response.choices[0].message.content.strip()

        # اگر سوال خیلی تخصصی بود → هدایت به سایت
        if "نمیتوانم" in answer or len(answer) < 15:
            answer = (
                "سؤال شما کمی تخصصی است ⚖️\n"
                "می‌توانید پاسخ دقیق و کامل را در سایت محضرباشی بخوانید:\n"
                "https://www.mahzarbashi.ir\n"
                "یا از مشاوره تلفنی با وکیل پایه یک استفاده کنید."
            )

        # پاسخ متنی
        await update.message.reply_text(answer)

        # پاسخ صوتی
        tts = gTTS(answer, lang='fa')
        tts.save("reply.mp3")
        await update.message.reply_voice(voice=open("reply.mp3", "rb"))

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("متاسفم، مشکلی در پردازش سؤال پیش آمد. لطفاً دوباره تلاش کنید.")

# هندلرها
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Flask route برای webhook
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok", 200

@app.route("/")
def index():
    return "🤖 Mahzarbashi Legal Assistant Bot is running."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TELEGRAM_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}"
    )
    app.run(host="0.0.0.0", port=port)
