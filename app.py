import os
import telebot
from flask import Flask, request
from openai import OpenAI
from gtts import gTTS
import tempfile

# متغیرهای محیطی
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

# پاسخ متنی از ChatGPT
def get_gpt_response(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "تو یک دستیار حقوقی دوستانه هستی که درباره قوانین ایران پاسخ می‌دهد."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ خطا در GPT: {e}")
        return "متأسفم، خطایی در دریافت پاسخ رخ داد. لطفاً دوباره تلاش کن."

# تولید صدا از متن
def text_to_voice(text):
    try:
        tts = gTTS(text=text, lang='fa')
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)
        return temp_file.name
    except Exception as e:
        print(f"❌ خطا در تبدیل صدا: {e}")
        return None

# پاسخ به پیام‌های متنی
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text
    reply_text = get_gpt_response(user_input)
    bot.reply_to(message, reply_text)

    # ارسال صوت
    voice_file = text_to_voice(reply_text)
    if voice_file:
        with open(voice_file, 'rb') as audio:
            bot.send_voice(message.chat.id, audio)
        os.remove(voice_file)

# مسیر وبهوک
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = request.get_data().decode("utf-8")
    bot.process_new_updates([telebot.types.Update.de_json(update)])
    return "OK", 200

@app.route("/", methods=["GET"])
def home():
    return "✅ Mahzarbashi Bot is running."

# اجرای برنامه
if __name__ == "__main__":
    bot.remove_webhook()
    render_url = os.getenv("RENDER_EXTERNAL_URL")
    if render_url:
        bot.set_webhook(url=f"{render_url}/{TELEGRAM_TOKEN}")
    app.run(host="0.0.0.0", port=10000)
