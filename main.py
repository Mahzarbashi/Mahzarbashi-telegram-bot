import os
import tempfile
import asyncio
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from gtts import gTTS

# -----------------------------
# دریافت توکن از محیط Render
# -----------------------------
TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not TOKEN:
    print("⚠️ متغیر محیطی TELEGRAM_TOKEN پیدا نشد! از توکن تستی استفاده می‌کنیم.")
    TOKEN = "8249435097:AAGOIS7GfwBayCTSZGFahbMhYcZDFxzSGAg"  # توکن موقت برای تست

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
# پاسخ متنی و دکمه صوتی
# -----------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first = update.effective_user.first_name
    text = update.message.text.strip()

    # پاسخ دوستانه و پیش‌فرض
    reply_text = f"😊 {user_first} عزیز!\n{START_TEXT}\n\nسؤالت: {text}\n\nجواب حقوقی: در حال بررسی… ⚖️"

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
# اجرای ربات با وبهوک روی Render
# -----------------------------
async def main():
    hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    if not hostname:
        raise ValueError("❌ متغیر محیطی RENDER_EXTERNAL_HOSTNAME پیدا نشد!")

    url = f"https://{hostname}/{TOKEN}"

    # ست کردن وبهوک
    await bot.set_webhook(url)
    print(f"✅ Webhook set to: {url}")

    # اجرای Application
    await application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        url_path=TOKEN,
        webhook_url=url
    )

# -----------------------------
# اجرا
# -----------------------------
if __name__ == "__main__":
    asyncio.run(main())
