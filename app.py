import os
import telebot
from gtts import gTTS
from io import BytesIO
import openai
import requests

# -------------------------
# Initial settings
# -------------------------

TELEGRAM_TOKEN = "8249435097:AAGOIS7GfwBayCTSZGFahbMhYcZDFxzSGAg"  # توکن شما
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# حذف خودکار وبهوک قدیمی
requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook")

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
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    return response.choices[0].message.content.strip()

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

    # Get legal answer
    answer_text = get_legal_answer(user_text)

    # Send text reply
    bot.send_message(chat_id, answer_text)

    # Generate and send voice reply
    audio_bytes = generate_voice(answer_text, voice_gender)
    bot.send_audio(chat_id, audio_bytes, title="پاسخ حقوقی")

# -------------------------
# Run bot
# -------------------------

if __name__ == "__main__":
    print("🚀 ربات محضرباشی هوشمند آماده است...")
    bot.infinity_polling()
