from io import BytesIO
from gtts import gTTS
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)

TELEGRAM_TOKEN = "8249435097:AAGOIS7GfwBayCTSZGFahbMhYcZDFxzSGAg"

# === بانک حقوقی داخلی ===
LEGAL_BANK = {
    "مدنی": {
        "مهریه": {
            "title": "مهریه و شرایط آن",
            "text": (
                "مَهریه و شرایط آن: مرد به هنگام اجرای صیغه نکاح، چیزی را به زنش می‌دهد "
                "که نشان‌دهنده قصد او برای نکاح باشد و در اصطلاح مَهریه یا صداق نامیده می‌شود.\n\n"
                "نحوه محاسبه مهریه: مثال: اگر مهریه ۱۱۰ سکه و ارزش هر سکه ۱۵ میلیون تومان باشد، "
                "کل مهریه = ۱۱۰ × ۱۵٫۰۰۰٫۰۰۰ = ۱٫۶۵۰٫۰۰۰٫۰۰۰ تومان."
            )
        },
        "اجاره": {
            "title": "قوانین اجاره",
            "text": "قوانین اجاره مسکن طبق قانون روابط موجر و مستأجر اجرا می‌شود. ..."
        }
    },
    "جزا": {
        "دیه": {
            "title": "دیه و مجازات‌ها",
            "text": "دیه و مجازات‌ها طبق قانون مجازات اسلامی تعیین می‌شود. ..."
        }
    }
}

CATEGORIES = list(LEGAL_BANK.keys())

# === توابع ربات ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(cat, callback_data=cat)] for cat in CATEGORIES] \
               + [[InlineKeyboardButton("مشاوره تخصصی", url="https://mahzarbashi.com/consult")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "سلام! من دستیار حقوقی محضرباشی هستم ✅\n"
        "می‌توانی موضوع موردنظر را از دکمه‌ها انتخاب کنی یا عنوان موضوع/شماره ماده را بپرسی.\n\n"
        "این ربات توسط نسترن بنی‌طبا ساخته شده است.",
        reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data
    if category in LEGAL_BANK:
        text = f"📚 موضوعات موجود در دسته {category}:\n"
        for topic in LEGAL_BANK[category]:
            text += f"- {topic}\n"
        await send_text_and_audio(query, text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    found = False
    for category, topics in LEGAL_BANK.items():
        for topic_name, topic_data in topics.items():
            if user_text == topic_name:
                answer = f"{topic_data['title']}\n\n{topic_data['text']}"
                await send_text_and_audio(update, answer)
                found = True
                break
        if found:
            break
    if not found:
        response = ("سوالت دریافت شد ✅\n"
                    "برای پاسخ تخصصی و جزئیات بیشتر لطفاً به سایت محضرباشی مراجعه کنید:\n"
                    "https://mahzarbashi.com/consult")
        await send_text_and_audio(update, response)

async def send_text_and_audio(update_or_query, text):
    if isinstance(update_or_query, Update):
        await update_or_query.message.reply_text(text)
    else:
        await update_or_query.edit_message_text(text)
    tts = gTTS(text=text, lang='fa')
    audio_fp = BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    if isinstance(update_or_query, Update):
        await update_or_query.message.reply_audio(audio_fp, filename="response.mp3")
    else:
        await update_or_query.message.reply_audio(audio_fp, filename="response.mp3")

# === اجرای ربات با Polling ===
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
