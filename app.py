# app.py
import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters
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
dispatcher = Dispatcher(bot, None, use_context=True)

# ---- دستور /start ----
def start(update, context):
    update.message.reply_text(
        "سلام! من ربات محضرباشی هستم. می‌توانم به سوالات حقوقی شما پاسخ بدهم.\n"
        "برای سوالات تخصصی، حتماً به سایت ما مراجعه کنید: www.mahzarbashi.ir"
    )

# ---- پاسخ به پیام‌ها ----
def handle_message(update, context):
    user_text = update.message.text

    # اگر سوال تخصصی باشد، هدایت به سایت
    if len(user_text) > 200 or any(word in user_text.lower() for word in ["قانون", "حقوق", "وکالت"]):
        reply_text = f"سوال شما تخصصی است. لطفاً برای پاسخ کامل به سایت مراجعه کنید: www.mahzarbashi.ir"
    else:
        # پاسخ هوش مصنوعی
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_text}],
            max_tokens=300
        )
        reply_text = response['choices'][0]['message']['content']

    update.message.reply_text(reply_text)

    # ساخت پاسخ صوتی
    tts = gTTS(text=reply_text, lang='fa')
    audio_path = f"voice_{update.message.message_id}.mp3"
    tts.save(audio_path)
    with open(audio_path, 'rb') as audio_file:
        update.message.reply_voice(audio_file)
    os.remove(audio_path)

# ---- افزودن هندلرها ----
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

# ---- وبهوک ----
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

@app.route("/")
def index():
    return "ربات محضرباشی فعال است ✅"

if __name__ == "__main__":
    app.run(port=5000)
