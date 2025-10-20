import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from gtts import gTTS
from io import BytesIO

# توکن واقعی ربات
TELEGRAM_TOKEN = "8249435097:AAGOIS7GfwBayCTSZGFahbMhYcZDFxzSGAg"

# پاسخ به دستور /start
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

# پاسخ به کلیک دکمه‌ها
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

# ارسال متن و فایل صوتی
async def send_text_and_audio(update_or_query, text):
    # ارسال متن
    if isinstance(update_or_query, Update):
        await update_or_query.message.reply_text(text)
    else:
        await update_or_query.edit_message_text(text)

    # تولید فایل صوتی
    tts = gTTS(text=text, lang='fa')
    audio_fp = BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)

    if isinstance(update_or_query, Update):
        await update_or_query.message.reply_audio(audio_fp, filename="response.mp3")
    else:
        await update_or_query.message.reply_audio(audio_fp, filename="response.mp3")

# پاسخ به پیام‌های متنی کاربر
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if "مهریه" in user_text:
        response = "مهریه طبق قانون مدنی محاسبه می‌شود. برای جزئیات بیشتر به سایت محضرباشی مراجعه کنید."
    else:
        response = "سوالت دریافت شد ✅\nبرای پاسخ تخصصی به سایت محضرباشی مراجعه کن."
    await send_text_and_audio(update, response)

# ساخت اپلیکیشن
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# اضافه کردن هندلرها
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# اجرای ربات
if __name__ == "__main__":
    app.run_polling()
