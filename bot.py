import os
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN", "8310741380:AAHRrADEytsjTVZYtJle71e5twxFxqr556c")

app = Flask(__name__)
flask_app = app  # برای gunicorn خیلی مهمه

# استارت بات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "سلام 👋\n"
        "به ربات محضرباشی خوش آمدید 🌐\n\n"
        "شما می‌توانید:\n"
        "📌 سوالات رایج را بپرسید\n"
        "🎙️ پاسخ صوتی دریافت کنید\n"
        "📝 درخواست مشاوره حقوقی ثبت کنید\n"
        "🌍 به وب‌سایت ما بروید\n\n"
        "لطفاً گزینه مورد نظر را انتخاب کنید."
    )
    await update.message.reply_text(welcome_text)

# مدیریت پیام‌های متنی
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if "مشاوره" in text:
        await update.message.reply_text("برای مشاوره حقوقی لطفاً از لینک زیر استفاده کنید:\nhttps://mahzarbashi.ir")
    elif "سایت" in text or "وبسایت" in text:
        await update.message.reply_text("ورود به سایت محضرباشی:\nhttps://mahzarbashi.ir")
    else:
        await update.message.reply_text("لطفاً گزینه‌های موجود را انتخاب کنید یا به سایت محضرباشی مراجعه کنید.")

# ساخت اپلیکیشن تلگرام
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put(update)
    return "ok"

@app.route('/')
def index():
    return "Mahzarbashi Bot is running successfully ✅"

if __name__ == '__main__':
    application.run_polling()
