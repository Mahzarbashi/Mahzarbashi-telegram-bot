import os
import threading
import json
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

# === Flask health endpoint ===
flask_app = Flask("health")

@flask_app.route("/")
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)

# === مسیر مطلق برای فایل legal_bank.json ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "legal_bank.json")

with open(file_path, "r", encoding="utf-8") as f:
    LEGAL_BANK = json.load(f)

# === دسته‌بندی‌های اصلی ===
CATEGORIES = list(LEGAL_BANK.keys())

# === توابع ربات ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(cat, callback_data=cat)] for cat in CATEGORIES
    ] + [[InlineKeyboardButton("مشاوره تخصصی", url="https://mahzarbashi.com/consult")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "سلام! من دستیار حقوقی محضرباشی هستم ✅\n"
        "می‌توانی موضوع موردنظر را از دکمه‌ها انتخاب کنی یا شماره ماده موردنظر را بپرسی.\n\n"
        "این ربات توسط نسترن بنی‌طبا ساخته شده است.",
        reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data
    if category in LEGAL_BANK:
        text = f"📚 مواد موجود در دسته {category}:\n"
        for mat in LEGAL_BANK[category]:
            text += f"- ماده {mat}\n"
        text += "\nبرای جزئیات می‌توانی شماره ماده را ارسال کنی."
        await send_text_and_audio(query, text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    found = False

    # بررسی اگر کاربر شماره ماده فرستاده باشد
    for category, materials in LEGAL_BANK.items():
        if user_text in materials:
            answer = materials[user_text]
            await send_text_and_audio(update, answer)
            found = True
            break

    if not found:
        # پاسخ عمومی برای سوال جدید یا خارج از بانک
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

    # تولید TTS فارسی
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
