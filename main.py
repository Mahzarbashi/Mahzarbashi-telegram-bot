import os
import tempfile
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from gtts import gTTS

# -----------------------------
# توکن تلگرام
# -----------------------------
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    print("⚠️ متغیر محیطی TELEGRAM_TOKEN پیدا نشد! از توکن تستی استفاده می‌کنیم.")
    TOKEN = "8249435097:AAGOIS7GfwBayCTSZGFahbMhYcZDFxzSGAg"

bot = Bot(token=TOKEN)

# -----------------------------
# پیام شروع
# -----------------------------
START_TEXT = (
    "🤖 این ربات توسط نسترن بنی‌طبا آماده شده است.\n"
    "📚 پاسخگوی سؤالات حقوقی شماست.\n"
    "سؤالتو بپرس تا با لحن دوستانه راهنماییت کنم 💬"
)

# -----------------------------
# پاسخ متنی حقوقی ساده بر اساس کلمات کلیدی
# -----------------------------
def legal_answer(text):
    text_lower = text.lower()
    if "ازدواج" in text_lower:
        return "📌 در ازدواج، شرط اصلی رضایت طرفین و اهلیت قانونی است."
    elif "طلاق" in text_lower:
        return "📌 طلاق بر اساس قانون ایران می‌تواند توافقی یا قضایی باشد."
    elif "قرارداد" in text_lower:
        return "📌 قرارداد باید دارای رضایت طرفین و موضوع مشروع باشد."
    elif "مهریه" in text_lower:
        return "📌 مهریه طبق قانون ایران مال مالی است که زن مالک آن می‌شود."
    else:
        return "⚖️ این موضوع نیاز به بررسی دقیق دارد. مشاوره تخصصی را در سایت محضرباشی دنبال کنید."

# -----------------------------
# پاسخ متنی و دکمه صوتی
# -----------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first = update.effective_user.first_name
    user_text = update.message.text.strip()

    answer_text = legal_answer(user_text)
    reply_text = f"😊 {user_first} عزیز!\n{START_TEXT}\n\nسؤالت: {user_text}\n\nجواب حقوقی: {answer_text}"

    # دکمه گوش دادن صوتی
    keyboard = [[InlineKeyboardButton("🎧 گوش دادن صوتی", callback_data=f"voice:{reply_text}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(reply_text, reply_markup=reply_markup)

# -----------------------------
# تولید و ارسال فایل صوتی
# -----------------------------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("voice:"):
        text = query.data.replace("voice:", "")
        tts = gTTS(text=text, lang='fa')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            await bot.send_audio(chat_id=query.message.chat_id, audio=open(tmp_file.name, 'rb'), title="پاسخ صوتی 🎵")

        await query.edit_message_text("✅ فایل صوتی برات فرستادم 🎵")

# -----------------------------
# راه‌اندازی Application
# -----------------------------
application = Application.builder().token(TOKEN).build()
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
application.add_handler(CallbackQueryHandler(button_handler))

# -----------------------------
# اجرای وبهوک مستقیم روی Render
# -----------------------------
if __name__ == "__main__":
    hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    if not hostname:
        raise ValueError("❌ متغیر محیطی RENDER_EXTERNAL_HOSTNAME پیدا نشد!")
    url = f"https://{hostname}/{TOKEN}"
    print(f"✅ Webhook set to: {url}")

    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        url_path=TOKEN,
        webhook_url=url
    )
