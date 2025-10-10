import os
import telebot
import pyttsx3
import re

TOKEN = os.getenv("BOT_TOKEN", "اینجا_توکن_بات_خودت")
bot = telebot.TeleBot(TOKEN)

# تابع بررسی اینکه سوال حقوقی هست یا نه
def is_legal_question(text):
    keywords = ["طلاق", "مهریه", "اجاره", "قرارداد", "ملک", "دادگاه", "قانون", "شکایت", "حقوقی"]
    return any(word in text for word in keywords)

# متن اصلی راهنما
def get_intro_message():
    return (
        "سلام دوست خوبم 🌸\n"
        "اینجا ربات محضرباشی هستم ✨\n"
        "می‌تونی سوال حقوقی‌ت رو بپرسی و من با زبانی ساده راهنمایی‌ت می‌کنم. "
        "اگر موضوعت تخصصی باشه، بهت پیشنهاد می‌کنم مستقیم با وکیل پایه یک صحبت کنی 👩‍⚖️👨‍⚖️.\n\n"
        "در سایت [mahzarbashi.ir](https://www.mahzarbashi.ir) "
        "هم می‌تونی راهنمایی بگیری و هم مشاوره تلفنی با وکیل پایه یک داشته باشی ☎️"
    )

# ساخت و ارسال صوت با pyttsx3 (خیلی سریع‌تر از gTTS)
def send_voice(chat_id, text):
    engine = pyttsx3.init()
    engine.save_to_file(text, "reply.mp3")
    engine.runAndWait()
    with open("reply.mp3", "rb") as voice:
        bot.send_voice(chat_id, voice)

# /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    text = get_intro_message()
    bot.send_message(message.chat.id, text, parse_mode="Markdown")
    send_voice(message.chat.id, text)

# پاسخ به پیام‌ها
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    if not is_legal_question(message.text):
        reply = "دوست عزیز 🌹 این ربات فقط به پرسش‌های حقوقی پاسخ می‌ده."
        bot.send_message(message.chat.id, reply)
        send_voice(message.chat.id, reply)
        return

    # اگر سوال حقوقی بود → جواب نمایشی (اینجا بعداً می‌تونیم GPT وصل کنیم)
    reply = f"سوالت رو دریافت کردم ✅\nموضوع: {message.text}\nپاسخ: این یک راهنمایی اولیه حقوقی است..."
    bot.send_message(message.chat.id, reply)
    send_voice(message.chat.id, reply)

bot.polling()
