import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import openai
from gtts import gTTS

# ---- تنظیم کلیدها ----
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise ValueError("❌ TELEGRAM_TOKEN یا OPENAI_API_KEY پیدا نشد. لطفاً Environment Variables را در Render چک کنید.")

openai.api_key = OPENAI_API_KEY
bot = Bot(token=TELEGRAM_TOKEN)
app = Flask(__name__)

# ---- ایجاد Application ----
application = Application.builder().token(TELEGRAM_TOKEN).build()

# ---- دستور /start ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! 👋\n"
        "من ربات *محضرباشی* هستم. می‌تونم به سوالات حقوقی شما پاسخ بدم.\n"
        "برای پرسش‌های تخصصی حتماً به سایت مراجعه کنید:\n"
        "👉 www.mahzarbashi.ir",
        parse_mode="Markdown"
    )

# ---- پاسخ به پیام‌ها ----
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    # اگر سوال تخصصی باشد → هدایت به سایت
    if len(user_text) > 200 or any(word in user_text.lower() for word in ["قانون", "حقوق", "وکالت"]):
        reply_text = "سوال شما تخصصی است. لطفاً برای پاسخ کامل به سایت مراجعه کنید: www.mahzarbashi.ir"
    else:
        # پاسخ هوش مصنوعی
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_text}],
            max_tokens=300
        )
        reply_text = response['choices'][0]['message']['content']

    # ارسال متن
    await update.message.reply_text(reply_text)

    # ساخت پاسخ صوتی
    tts = gTTS(text=reply_text, lang='fa')
    audio_path = f"voice_{update.message.message_id}.mp3"
    tts.save(audio_path)
    with open(audio_path, 'rb') as audio_file:
        await update.message.reply_voice(audio_file)
    os.remove(audio_path)

# ---- افزودن هندلرها ----
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

# ---- وبهوک ----
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.run_update(update)
    return "OK"

@app.route("/")
def index():
    return "ربات محضرباشی فعال است ✅"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
