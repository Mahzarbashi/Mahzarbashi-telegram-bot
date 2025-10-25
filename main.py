import os
from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    InputFile
)
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler, 
    ContextTypes, 
    filters
)
from gtts import gTTS
import tempfile

# 🟢 توکن ربات
TOKEN = os.getenv("BOT_TOKEN", "8249435097:AAGOIS7GfwBayCTSZGFahbMhYcZDFxzSGAg")

# 🟢 شروع گفتگو
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first = update.effective_user.first_name
    text = f"سلام {user_first} 🌷\nمن دستیار حقوقی محضرباشی‌ام 🤖\nسؤالت رو بنویس تا باهم بررسیش کنیم 💬"
    await update.message.reply_text(text)

# 🟢 پاسخ متنی با دکمه پخش صوت
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text

    response_text = (
        f"📘 پاسخ حقوقی:\n"
        f"سؤالت دریافت شد ✅\n"
        f"برای جزئیات بیشتر می‌تونی به سایت محضرباشی سر بزنی 🌐\n"
        f"https://mahzarbashi.com/consult\n\n"
        f"اگه خواستی همین پاسخ رو به‌صورت صوتی گوش بدی، روی دکمه زیر بزن 🎧"
    )

    keyboard = [
        [InlineKeyboardButton("🔊 پخش صوت پاسخ", callback_data=f"voice|{user_msg}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(response_text, reply_markup=reply_markup)

# 🟢 تبدیل پاسخ به صوت
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("voice|"):
        user_question = data.split("|", 1)[1]
        text = f"پاسخ خلاصه به سؤالت:\n{user_question}\nبه صورت صوتی برات خونده میشه 🎙️"
        await query.edit_message_text(text="🔊 در حال تولید صدای پاسخ...")

        tts = gTTS(text=text, lang='fa')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            await query.message.reply_audio(audio=InputFile(tmp_file.name, filename="reply.mp3"))

# 🟢 اجرای ربات
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))

    print("🤖 ربات محضرباشی با موفقیت اجرا شد و آماده دریافت پیام‌هاست!")
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        url_path=TOKEN,
        webhook_url=f"https://mahzarbashi.onrender.com/{TOKEN}"
    )
