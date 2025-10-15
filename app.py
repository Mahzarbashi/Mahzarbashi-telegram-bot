import os
import telebot
from flask import Flask, request
import openai
from gtts import gTTS
import tempfile

# ---------------------- تنظیمات اولیه ----------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = "8249435097:AAGOIS7GfwBayCTSZGFahbMhYcZDFxzSGAg"

openai.api_key = OPENAI_API_KEY
bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# ---------------------- پاسخ ChatGPT ----------------------
def get_gpt_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "تو یک دستیار حقوقی دوستانه و دقیق هستی که به پرسش‌های کاربران درباره قوانین ایران پاسخ می‌دهد."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("❌ خطا در OpenAI:", e)
        return "متأسفم، خطایی در دریافت پاسخ رخ داد. لطفاً دوباره تلاش کن."

# ---------------------- تبدیل متن به صدا ----------------------
def text_to_voice(text):
    try:
        tts = gTTS(text=text, lang='fa')
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)
        return temp_file.name
    except Exception as e:
        print("❌ خطا در تولید صدا:", e)
        return None

# ---------------------- پاسخ‌دهی به پیام‌ها ----------------------
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    user_text = message.text
    reply = get_gpt_response(user_text)
    bot.reply_to(message, reply)

    voice_path = text_to_voice(reply)
    if voice_path:
        with open(voice_path, "rb") as audio:
            bot.send_voice(message.chat.id, audio)
        os.remove(voice_path)

# ---------------------- مسیر Webhook ----------------------
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    json_update = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_update)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/", methods=["GET"])
def home():
    return "✅ Bot is alive", 200

if __name__ == "__main__":
    # حذف وبهوک قبلی
    bot.remove_webhook()
    # ست کردن وبهوک به آدرس پروژه‌ی شما
    bot.set_webhook(url=f"https://mahzarbashi-telegram-bot-3-mmjb.onrender.com/{TELEGRAM_TOKEN}")
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
