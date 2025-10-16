import os
import telebot
from flask import Flask, request
import openai
from gtts import gTTS
import tempfile

# ---------------------- تنظیمات ----------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = "8249435097:AAGOIS7GfwBayCTSZGFahbMhYcZDFxzSGAg"

openai.api_key = OPENAI_API_KEY
bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# ---------------------- پاسخ OpenAI ----------------------
def get_gpt_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "تو یک دستیار حقوقی دوستانه و دقیق هستی که به پرسش‌های کاربران درباره قوانین ایران پاسخ می‌دهی."},
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

# ---------------------- پاسخ به پیام‌ها ----------------------
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

# ---------------------- مسیر وب‌هوک ----------------------
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    json_update = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_update)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/", methods=["GET"])
def home():
    return "✅ Mahzarbashi Bot is live!", 200

# ---------------------- اجرای نهایی ----------------------
if __name__ == "__main__":
    bot.remove_webhook()  # حذف وب‌هوک قدیمی
    render_url = os.getenv("RENDER_EXTERNAL_URL")
    if render_url:
        bot.set_webhook(url=f"{render_url}/{TELEGRAM_TOKEN}")
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    from flask import Flask, request
import openai, os

app = Flask(__name__)

@app.route("/test_openai")
def test_openai():
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            return "❌ OPENAI_API_KEY not found in environment."

        # یک تست کوتاه برای بررسی اتصال
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "سلام"}]
        )
        return "✅ OpenAI connection successful!"
    except Exception as e:
        return f"❌ Error: {str(e)}"
