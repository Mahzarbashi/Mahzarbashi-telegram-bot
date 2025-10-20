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

# === Flask برای health endpoint ===
flask_app = Flask("health")

@flask_app.route("/")
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)

# === بانک حقوقی نمونه ===
LEGAL_FAQ = {
    "مهریه": {
        "سوالات": [
            "مهریه چگونه محاسبه می‌شود؟",
            "شرایط پرداخت مهریه چیست؟"
        ],
        "پاسخ‌ها": [
            "مهریه طبق قانون مدنی محاسبه می‌شود. برای جزئیات بیشتر به سایت محضرباشی مراجعه کنید.",
            "مهریه می‌تواند نقدی یا غیرنقدی باشد، و زمان و نحوه پرداخت طبق ماده ۱۰۷۸ قانون مدنی مشخص می‌شود."
        ]
    },
    "قراردادها": {
        "سوالات": ["فسخ قرارداد چگونه انجام می‌شود؟"],
        "پاسخ‌ها": ["فسخ قرارداد طبق قانون مدنی و شرایط قراردادی انجام می‌شود. برای جزئیات به سایت محضرباشی مراجعه کنید."]
    },
    "اجاره": {
        "سوالات": ["قوانین اجاره مسکن چیست؟"],
        "پاسخ‌ها": ["قوانین اجاره طبق قانون مدنی و قانون روابط موجر و مستأجر انجام می‌شود. برای جزئیات به سایت محضرباشی مراجعه کنید."]
    },
    "جزا": {
        "سوالات": ["دیه و مجازات‌ها چگونه است؟"],
        "پاسخ‌ها": ["قوانین جزا طبق قانون مجازات اسلامی است. برای جزئیات به سایت محضرباشی مراجعه کنید."]
    }
}

# === توابع ربات ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("مهریه", callback_data="مهریه")],
        [InlineKeyboardButton("قراردادها", callback_data="قراردادها")],
        [InlineKeyboardButton("اجاره", callback_data="اجاره")],
        [InlineKeyboardButton("جزا", callback_data="جزا")],
        [InlineKeyboardButton("مشاوره تخصصی", url="https://mahzarbashi.com/consult")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "سلام! من دستیار حقوقی محضرباشی هستم ✅\n"
        "می‌تونی موضوع موردنظر رو از دکمه‌ها انتخاب کنی یا سوال خودت رو بپرسی.\n\n"
        "این ربات توسط نسترن بنی‌طبا ساخته شده است.",
        reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data
    if category in LEGAL_FAQ:
        faq = LEGAL_FAQ[category]
        text = "📚 سوالات رایج:\n"
        for i, q in enumerate(faq["سوالات"], 1):
            text += f"{i}. {q}\n"
        text += "\nبرای جزئیات می‌توانی روی سوال خودت پیام بدهی یا به سایت محضرباشی مراجعه کن."
        await send_text_and_audio(query, text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text or ""
    found = False
    # بررسی سوالات پیش‌فرض
    for category, faq in LEGAL_FAQ.items():
        for q, a in zip(faq["سوالات"], faq["پاسخ‌ها"]):
            if q.strip("؟").replace(" ", "") in user_text.replace(" ", ""):
                await send_text_and_audio(update, a)
                found = True
                break
        if found:
            break
    if not found:
        # پاسخ عمومی برای سوال جدید
        response = ("سوالت دریافت شد ✅\n"
                    "برای پاسخ تخصصی و جزئیات بیشتر لطفاً به سایت محضرباشی مراجعه کنید:\n"
                    "https://mahzarbashi.com/consult")
        await send_text_and_audio(update, response)

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
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    start_flask_and_bot()
