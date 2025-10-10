import os
import telebot
from flask import Flask, request
import pyttsx3

TOKEN = os.getenv("BOT_TOKEN", "اینجا_توکن_خودت")
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# فیلتر سوالات حقوقی
def is_legal_question(text):
    keywords = ["طلاق", "مهریه", "اجاره", "قرارداد", "ملک", "دادگاه", "قانون", "شکایت", "حقوقی"]
    return any(word in text for word in keywords)

# ارسال صوت با pyttsx3
def send_voice(chat_id, text):
    engine = pyttsx3.init()
    engine.save_to_file(text, "reply.mp3")
    engine.runAndWait()
    with open("reply.mp3", "rb") as voice:
        bot.send_voice(chat_id, voice)

# پیام خوشامد
def get_intro_message():
    return (
        "سلام دوست خوبم 🌸\n"
        "من ربات محضرباشی هستم ✨\n"
        "می‌تونی سوال حقوقی‌ت رو بپرسی و من با زبانی ساده راهنمایی‌ت می‌کنم. "
        "اگر موضوعت تخصصی باشه، بهت پیشنهاد می‌کنم مستقیم با وکیل پایه یک صحبت کنی 👩‍⚖️👨‍⚖️.\n\n"
        "در سایت [mahzarbashi.ir](https://www.mahzarbashi.ir) "
        "هم می‌تونی راهنمایی بگیری و هم مشاوره تلفنی با وکیل پایه یک داشته باشی ☎️"
    )

# هندلر /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    text = get_intro_message()
    bot.send_message(message.chat.id, text, parse_mode="Markdown")
    send_voice(message.chat.id, text)

# هندلر پیام‌ها
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    if not is_legal_question(message.text):
        reply = "دوست عزیز 🌹 این ربات فقط به پرسش‌های حقوقی پاسخ می‌ده."
        bot.send_message(message.chat.id, reply)
        send_voice(message.chat.id, reply)
        return

    reply = f"سوالت رو دریافت کردم ✅\nموضوع: {message.text}\nپاسخ: این یک راهنمایی اولیه حقوقی است..."
    bot.send_message(message.chat.id, reply)
    send_voice(message.chat.id, reply)

# وبهوک
@app.route("/" + TOKEN, methods=["POST"])
def getMessage():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "ok", 200

@app.route("/", methods=["GET"])
def index():
    return "Mahzarbashi Bot is running ✅", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
