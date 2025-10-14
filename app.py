import os
import threading
import time
from io import BytesIO

import telebot
from gtts import gTTS
from flask import Flask
from openai import OpenAI

# -------------------------
# Environment Variables
# -------------------------
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise Exception("TELEGRAM_TOKEN یا OPENAI_API_KEY در Environment Variables ست نشده است!")

# -------------------------
# Initialize clients
# -------------------------
bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

# -------------------------
# Delete existing webhook to avoid 409
# -------------------------
try:
    import requests
    resp = requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook", timeout=5)
    print("Webhook delete response:", resp.json())
except Exception as e:
    print("Error deleting webhook:", e)

# -------------------------
# User preferences for voice
# -------------------------
user_preferences = {}
VOICE_OPTIONS = {"زن": "female", "مرد": "male"}

# -------------------------
# Welcome & about messages
# -------------------------
WELCOME_MSG = (
    "سلام 👋 من دستیار حقوقی محضرباشی هستم.\n"
    "می‌تونم درباره‌ی طلاق، ازدواج، ارث، قرارداد، سند و سایر موضوعات حقوقی راهنماییت کنم.\n"
    "برای مشاوره تخصصی هم می‌تونی به سایت www.mahzarbashi.ir سر بزنی."
)
ABOUT_MSG = (
    "توسعه‌دهنده: نسترن بنی‌طبا\n"
    "دستیار حقوقی هوشمند، پاسخگو به سؤالات حقوقی عمومی، همراه با پاسخ صوتی"
)

# -------------------------
# Voice selection
# -------------------------
def ask_voice_selection(chat_id):
    msg = bot.send_message(chat_id, "لطفاً صدای پاسخ‌هایت را انتخاب کن:\nزن یا مرد")
    bot.register_next_step_handler(msg, set_user_voice)

def set_user_voice(message):
    chat_id = message.chat.id
    choice = message.text.strip()
    if choice in VOICE_OPTIONS:
        user_preferences[chat_id] = VOICE_OPTIONS[choice]
        bot.send_message(chat_id, f"صدای '{choice}' انتخاب شد. حالا می‌تونی سؤال حقوقی خودت رو بپرسی.")
    else:
        bot.send_message(chat_id, "لطفاً فقط 'زن' یا 'مرد' وارد کن.")
        ask_voice_selection(chat_id)

# -------------------------
# Voice generation
# -------------------------
def generate_voice(text, voice_gender):
    tts = gTTS(text=text, lang='fa', tld='com')
    audio_bytes = BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    return audio_bytes

# -------------------------
# Legal answer
# -------------------------
def get_legal_answer(question, retries=3, delay=2):
    prompt = (
        f"شما یک دستیار حقوقی هستید. پاسخ دوستانه و کوتاه به فارسی بده. "
        f"اگر سؤال تخصصی بود، به سایت محضرباشی: www.mahzarbashi.ir ارجاع بده.\n"
        f"سؤال: {question}"
    )
    for attempt in range(1, retries + 1):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI error attempt {attempt}: {e}")
            if attempt < retries:
                time.sleep(delay)
            else:
                return "متأسفم، خطایی در دریافت پاسخ رخ داد. لطفاً دوباره تلاش کن."

# -------------------------
# Telegram handlers
# -------------------------
@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, WELCOME_MSG)
    bot.send_message(chat_id, ABOUT_MSG)
    ask_voice_selection(chat_id)

@bot.message_handler(commands=['about'])
def handle_about(message):
    bot.send_message(message.chat.id, ABOUT_MSG)

@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    user_text = message.text.strip()
    voice_gender = user_preferences.get(chat_id, 'female')

    print(f"Received message from {chat_id}: {user_text}")

    answer_text = get_legal_answer(user_text)

    try:
        bot.send_message(chat_id, answer_text)
    except Exception as e:
        print("Error sending text message:", e)

    try:
        audio_bytes = generate_voice(answer_text, voice_gender)
        bot.send_audio(chat_id, audio_bytes, title="پاسخ حقوقی")
    except Exception as e:
        print("Error sending audio:", e)

# -------------------------
# Polling thread
# -------------------------
def start_telebot_polling():
    print("Starting telebot polling thread...")
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print("Polling exception:", e)
            time.sleep(3)

threading.Thread(target=start_telebot_polling, daemon=True).start()

# -------------------------
# Flask app to bind PORT on Render
# -------------------------
from flask import Flask
app = Flask(__name__)

@app.route("/")
def index():
    return {"status": "ok", "bot": "mahzarbashi"}

@app.route("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting Flask app on port {port}...")
    app.run(host="0.0.0.0", port=port)
