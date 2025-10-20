import os
import threading
from io import BytesIO
from gtts import gTTS
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)

# === توکن ربات ===
TELEGRAM_TOKEN = "8249435097:AAGOIS7GfwBayCTSZGFahbMhYcZDFxzSGAg"

# === Flask برای health endpoint (Render نیاز دارد به پورت) ===
flask_app = Flask("health")

@flask_app.route("/")
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)

# === توابع ربات ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("سوالات حقوقی رایج", callback_data="faq")],
        [InlineKeyboardButton("مشاوره تخصصی", url="https://mahzarbashi.com/consult")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "سلام! من دستیار حقوقی محضرباشی هستم ✅\n"
        "می‌تونی از من سوال حقوقی بپرسی یا به مشاوره تخصصی سایت مراجعه کنی.",
        reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "faq":
        text = (
            "📚 سوالات رایج حقوقی:\n"
            "1. مهریه چگونه محاسبه می‌شود؟\n"
            "2. فسخ قرارداد به چه صورت انجام می‌شود؟\n"
            "3. قوانین اجاره مسکن چیست؟\n\n"
            "برای پاسخ کامل به سایت محضرباشی مراجعه کنید."
        )
        await send_text_and_audio(query, text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text or ""
    if "مهریه" in user_text:
        response = "مهریه طبق قانون مدنی محاسبه می‌شود. برای جزئیات بیشتر به سایت محضرباشی مراجعه کنید."
    else:
        response = "سوالت دریافت شد ✅\nبرای پاسخ تخصصی به سایت محضرباشی مراجعه کن."
    await send_text_and_audio(update, response)

# ارسال متن و صوت
async def send_text_and_audio(update_or_query, text):
    # ارسال متن
    if isinstance(update_or_query, Update):
        await update_or_query.message.reply_text(text)
    else:
        await update_or_query.edit_message_text(text)

    # تولید TTS
    tts = gTTS(text=text, lang='fa')
    audio_fp = BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)

    if isinstance(update_or_query, Update):
        await update_or_query.message.reply_audio(audio_fp, filename="response.mp3")
    else:
        await update_or_query.message.reply_audio(audio_fp, filename="response.mp3")

# === اجرای Flask و Telegram همزمان ===
def start_flask_and_bot():
    # اجرا Flask در background thread برای باز کردن پورت
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()

    # اجرای ربات تلگرام (polling)
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()  # blocking call

if __name__ == "__main__":
    start_flask_and_bot()
