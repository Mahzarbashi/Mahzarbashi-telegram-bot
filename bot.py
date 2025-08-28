from flask import Flask, request
import telegram

# توکن ربات محضرباشی
TOKEN = "8453972361:AAGUXQ7ii4ujwm9Of04UeyzhSabMNM8QYMs"
bot = telegram.Bot(token=TOKEN)

# ساخت اپلیکیشن Flask
app = Flask(__name__)

# تعریف سوالات و پاسخ‌های آماده
faq = {
    "طلاق": "برای طلاق توافقی باید به دفاتر خدمات قضایی مراجعه کنید و مدارک کامل داشته باشید.",
    "مهریه": "مهریه حق قانونی زن است و در هر زمانی قابل مطالبه است.",
    "حضانت": "حضانت فرزند تا ۷ سالگی با مادر است، مگر اینکه دادگاه تصمیم دیگری بگیرد.",
    "سند": "برای انتقال سند رسمی باید به دفترخانه اسناد رسمی مراجعه کنید."
}

@app.route(f'/{TOKEN}', methods=['POST'])
def respond():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    message = update.message.text.strip()

    # اگر کاربر /start فرستاد
    if message == "/start":
        bot.sendMessage(
            chat_id=chat_id,
            text="سلام آوین جان 🌿\nبه ربات محضرباشی خوش اومدی! ✅\nسوال حقوقی‌ات رو بپرس:"
        )
    # اگر سوال کاربر داخل FAQ بود
    elif message in faq:
        bot.sendMessage(chat_id=chat_id, text=faq[message])
    else:
        bot.sendMessage(chat_id=chat_id, text="سوالت تخصصی هست 🌿\nبرای پاسخ دقیق‌تر به سایت محضرباشی برو:\nhttps://mahzarbashi.ir")

    return "ok"

@app.route('/')
def index():
    return "ربات محضرباشی فعال است ✅"

if __name__ == '__main__':
    app.run(threaded=True)
