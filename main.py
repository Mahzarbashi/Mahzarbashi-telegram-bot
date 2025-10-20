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

# === Flask health endpoint ===
flask_app = Flask("health")

@flask_app.route("/")
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)

# === بانک حقوقی پیشرفته داخلی ===
LEGAL_BANK = {
    "مدنی": {
        "مهریه": {
            "title": "مهریه و شرایط آن",
            "text": (
                "مَهریه و شرایط آن: مرد به هنگام اجرای صیغه نکاح، چیزی را به زنش می‌دهد "
                "که نشان‌دهنده قصد او برای نکاح باشد و در اصطلاح مَهریه یا کابین یا صداق نامیده می‌شود. "
                "این هدیه و بخشش که از طرف مرد انجام می‌شود، امروزه به هدف پایبندی به لوازم زندگی مشترک "
                "و ارتباط زناشویی یا ضامنی برای حق طلاق زن درآمده است.\n\n"
                "نحوه محاسبه مهریه:\n"
                "مهریه معمولاً به صورت عدد مشخص یا سکه طلا تعیین می‌شود. "
                "مثال: اگر مهریه ۱۱۰ سکه باشد و ارزش هر سکه امروز ۱۵ میلیون تومان باشد، "
                "کل مهریه = ۱۱۰ × ۱۵٫۰۰۰٫۰۰۰ = ۱٫۶۵۰٫۰۰۰٫۰۰۰ تومان خواهد بود. "
                "در صورت عدم توانایی پرداخت یکجا، مهریه طبق قانون امکان پرداخت قسطی دارد."
            )
        },
        "اجاره": {
            "title": "قوانین اجاره مسکن",
            "text": (
                "قوانین اجاره مسکن طبق قانون روابط موجر و مستأجر اجرا می‌شود. "
                "قرارداد اجاره باید شامل مشخصات طرفین، مبلغ اجاره، مدت اجاره و شرایط فسخ باشد.\n\n"
                "نکات مهم:\n"
                "1. اجاره‌بها باید به صورت توافقی یا مطابق تعرفه‌های قانونی باشد.\n"
                "2. تخلیه ملک و دریافت ودیعه طبق ماده‌های قانونی انجام می‌شود.\n"
                "3. در صورت عدم پرداخت، موجر حق دارد مطابق قانون اقدام کند."
            )
        },
        "قرارداد": {
            "title": "فسخ قرارداد و شرایط آن",
            "text": (
                "فسخ قرارداد طبق قانون مدنی و شرایط قراردادی انجام می‌شود. "
                "در صورتی که طرفین شرایط قرارداد را رعایت نکنند، می‌توانند آن را فسخ کنند.\n\n"
                "نکات مهم:\n"
                "1. فسخ باید کتبی یا با توافق طرفین انجام شود.\n"
                "2. خسارات ناشی از فسخ طبق ماده‌های مربوطه قابل مطالبه است."
            )
        }
    },
    "جزا": {
        "دیه": {
            "title": "دیه و مجازات‌ها",
            "text": (
                "دیه و مجازات‌ها طبق قانون مجازات اسلامی تعیین می‌شود. "
                "میزان دیه بسته به نوع جراحت و مقتول متفاوت است.\n\n"
                "مثال:\n"
                "1. دیه کامل انسان بالغ = ۱۰۰ میلیون تومان (طبق تعرفه سال جاری)\n"
                "2. دیه نقص عضو یا جراحات جزئی طبق جدول قانونی محاسبه می‌شود."
            )
        }
    }
}

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
        "می‌توانی موضوع موردنظر را از دکمه‌ها انتخاب کنی یا عنوان موضوع/شماره ماده موردنظر را بپرسی.\n\n"
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
        text += "\nبرای جزئیات می‌توانی عنوان موضوع را ارسال کنی."
        await send_text_and_audio(query, text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    found = False

    # جستجو در بانک پیشرفته
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
        # پاسخ عمومی برای سوال خارج از بانک
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
