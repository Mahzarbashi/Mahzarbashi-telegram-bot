import os import telebot from gtts import gTTS from io import BytesIO from openai import OpenAI

-------------------------

تنظیمات اولیه

-------------------------

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN') OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN) client = OpenAI(api_key=OPENAI_API_KEY)

دیتابیس ساده برای انتخاب صدا و ذخیره کاربرها

user_preferences = {}

-------------------------

پیام خوش آمد

-------------------------

WELCOME_MSG = ( "سلام 👋 من دستیار حقوقی محضرباشی هستم.\n" "می‌تونم درباره‌ی طلاق، ازدواج، ارث، قرارداد، سند و سایر موضوعات حقوقی راهنماییت کنم.\n" "برای مشاوره تخصصی هم می‌تونی به سایت www.mahzarbashi.ir سر بزنی." )

ABOUT_MSG = ( "توسعه‌دهنده: نسترن بنی‌طبا\n" "دستیار حقوقی هوشمند، پاسخگو به سؤالات حقوقی عمومی، همراه با پاسخ صوتی" )

-------------------------

انتخاب صدا

-------------------------

VOICE_OPTIONS = {"زن": "female", "مرد": "male"}

def ask_voice_selection(chat_id): msg = bot.send_message(chat_id, "لطفاً صدای پاسخ‌هایت را انتخاب کن:\nزن یا مرد") bot.register_next_step_handler(msg, set_user_voice)

def set_user_voice(message): chat_id = message.chat.id choice = message.text.strip() if choice in VOICE_OPTIONS: user_preferences[chat_id] = VOICE_OPTIONS[choice] bot.send_message(chat_id, f"صدای '{choice}' انتخاب شد. حالا می‌تونی سؤال حقوقی خودت رو بپرسی.") else: bot.send_message(chat_id, "لطفاً فقط 'زن' یا 'مرد' وارد کن.") ask_voice_selection(chat_id)

-------------------------

تولید پاسخ صوتی

-------------------------

def generate_voice(text, voice_gender): tts = gTTS(text=text, lang='fa', tld='com')  # gTTS فقط جنس صدا پیش‌فرض دارد، اینجا پیش‌فرض زن/مرد را مدیریت میکنیم audio_bytes = BytesIO() tts.write_to_fp(audio_bytes) audio_bytes.seek(0) return audio_bytes

-------------------------

پاسخ به سوالات حقوقی

-------------------------

LEGAL_KEYWORDS = ['مهریه','طلاق','ارث','قرارداد','سند']

def get_legal_answer(question): prompt = ( f"شما یک دستیار حقوقی هستید. پاسخ دوستانه و کوتاه به فارسی بده. " f"اگر سؤال تخصصی بود، به سایت محضرباشی: www.mahzarbashi.ir ارجاع بده. \n" f"سؤال: {question}" ) response = client.chat.completions.create( model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}], max_tokens=500 ) return response.choices[0].message.content.strip()

-------------------------

هندلر پیام‌ها

-------------------------

@bot.message_handler(commands=['start']) def handle_start(message): chat_id = message.chat.id bot.send_message(chat_id, WELCOME_MSG) bot.send_message(chat_id, ABOUT_MSG) ask_voice_selection(chat_id)

@bot.message_handler(commands=['about']) def handle_about(message): bot.send_message(message.chat.id, ABOUT_MSG)

@bot.message_handler(func=lambda m: True) def handle_all_messages(message): chat_id = message.chat.id user_text = message.text.strip() voice_gender = user_preferences.get(chat_id, 'female')

# گرفتن پاسخ حقوقی
answer_text = get_legal_answer(user_text)

# ارسال پاسخ نوشتاری
bot.send_message(chat_id, answer_text)

# تولید و ارسال صوتی
audio_bytes = generate_voice(answer_text, voice_gender)
bot.send_audio(chat_id, audio_bytes, title="پاسخ حقوقی")

-------------------------

اجرای ربات

-------------------------

if name == 'main': print("ربات محضرباشی هوشمند آماده است...") bot.infinity_polling()

