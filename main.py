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
TOKEN = os.getenv("BOT_TOKEN", "932785959:AAGR9Z_g87RUwuGygcx76lPG5i725jT52TM")

# 🟢 دستور شروع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first = update.effective_user.first_name
    text = f"سلام {user_first} 🌷\nمن دستیار حقوقی محضرباشی هستم 🤖\nسؤالت رو بنویس تا کمکت کنم 💬"
    await update.message.reply_text(text)

# 🟢 پاسخ متنی و دکمه‌ی پخش صوت
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text

    # پاسخ ساده (در آینده می‌تونه با هوش مصنوعی پاسخ بده)
    response_text = f"📘 پاسخ حقوقی: \nسؤال شما دریافت شد ✅\n\nاگر خواستی همین پاسخ رو به‌صورت صوتی گوش بدی، دکمه زیر رو بزن 🎧"

    keyboard = [
        [InlineKeyboardButton("🔊 پخش صوت", callback_data=f"voice|{user_msg}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(response_text, reply_markup=reply_markup)

# 🟢 تبدیل پاسخ به صوت در صورت درخواست
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("voice|"):
        text = "این پاسخ به صورت صوتی برات خونده میشه 🎙️"
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

    print("🤖 Bot is running and ready for messages!")
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        url_path=TOKEN,
        webhook_url=f"https://mahzarbashi.onrender.com/{TOKEN}"
    )
