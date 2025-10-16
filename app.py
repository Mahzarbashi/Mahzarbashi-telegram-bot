import os
import telebot
import openai
from flask import Flask, request, jsonify
from gtts import gTTS

# ==========================
# تنظیم کلیدها از Environment Variables
# ==========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise ValueError("❌ TELEGRAM_TOKEN یا OPENAI_API_KEY یافت نشد. لطفاً در Render تنظیم شوند.")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

# ==========================
# Flask App
# ==========================
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Mahzarbashi Assistant Bot is running successfully!"

@app.route("/test_openai")
def test_openai():
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "سلام"}]
        )
        return "✅ OpenAI connection successful!"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ==========================
# Webhook endpoint برای Telegram
# ==========================
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    json_update = request.get_json(force=True)
    update = telebot.types.Update.de_json(json_update)
    bot.process_new_updates([update])
    return "ok", 200

# ==========================
# هندلر پیام‌ها
# ==========================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        "سلام 👋\nمن دستیار حقوقی محضرباشی هستم.\nبرای شروع فقط کافیه سوالت رو تایپ کنی تا پاسخ نوشتاری و صوتی بگیری 💬🎧"
    )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        user_text = message.text.strip()

        # درخواست به OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "تو یک مشاور حقوقی با لحن دوستانه و مطمئن هستی."},
                {"role": "user", "content": user_text}
            ]
        )

        reply_text = response.choices[0].message['content']

        # ارسال پاسخ متنی
        bot.reply_to(message, reply_text)

        # تولید پاسخ صوتی
        tts = gTTS(reply_text, lang='fa')
        audio_file = f"reply_{message.chat.id}.mp3"
        tts.save(audio_file)
        with open(audio_file, "rb") as audio:
            bot.send_audio(message.chat.id, audio)
        os.remove(audio_file)

    except Exception as e:
        bot.reply_to(message, f"متأسفم، خطایی رخ داد:\n{str(e)}")

# ==========================
# اجرای سرور Flask
# ==========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
