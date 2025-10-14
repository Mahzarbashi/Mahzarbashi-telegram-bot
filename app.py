import os
import threading
import time
import telebot
from gtts import gTTS
from io import BytesIO
import openai
import requests
from flask import Flask

# -------------------------
# Initial settings
# -------------------------

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8249435097:AAGOIS7GfwBayCTSZGFahbMhYcZDFxzSGAg")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# -------------------------
# Delete existing webhook
# -------------------------
try:
    print("Deleting any existing webhook...")
    resp = requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook", timeout=5)
    print("Webhook delete response:", resp.json())
except Exception as e:
    print("Error deleting webhook:", e)

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

# Simple database for voice preferences
user_preferences = {}

# -------------------------
# Welcome messages
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

VOICE_OPTIONS = {"زن": "female", "مرد": "male"}

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
# Legal answers
# -------------------------

LEGAL_KEYWORDS = ['مهریه', 'طلاق', 'ارث', 'قرارداد', 'سند']

def get_legal_answer(question):
    prompt = (
        f"شما یک دستیار حقوقی هستید. پاسخ دوستانه و کوتاه به فارسی بده. "
        f"اگر سؤال تخصصی بود، به سایت محضرباشی: www.mahzarbashi.ir ارجاع بده.\n"
        f"سؤال: {question}"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("OpenAI error:", e)
        return "متأسفم، خطایی در دریافت پاسخ رخ داد. لطفاً دوباره تلاش کن."

# -------------------------
# Message handlers
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
    
    # Send text reply
    try:
        bot.send_message(chat_id, answer_text)
    except Exception as e:
        print("Error sending text message:", e)

    # Generate and send voice reply
    try:
        audio_bytes = generate_voice(answer_text, voice_gender)
        bot.send_audio(chat_id, audio_bytes, title="پاسخ حقوقی")
    except Exception as e:
        print("Error sending audio:", e)

# -------------------------
# Run bot in background thread (polling)
# -------------------------

def start_telebot_polling():
    print("Starting telebot polling thread...")
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print("Polling exception:", e)
            time.sleep(3)

polling_thread = threading.Thread(target=start_telebot_polling, daemon=True)
polling_thread.start()

# -------------------------
# Minimal Flask app to bind PORT for Render
# -------------------------

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
