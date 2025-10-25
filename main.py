import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from gtts import gTTS

# تنظیمات لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# دریافت توکن از محیط Render
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ توکن تلگرام پیدا نشد! لطفاً در Render مقدار TELEGRAM_BOT_TOKEN را تنظیم کنید.")

# ساخت اپلیکیشن
app = Application.builder().token(TOKEN).build()

# پیام شروع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🗣 دریافت صوتی پاسخ", callback_data="voice_mode")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "سلام 🌸 من ربات محضرباشی هستم!\n"
        "سؤالت رو بنویس تا بهت جواب بدم 👩‍⚖️",
        reply_markup=reply_markup
    )

# پاسخ به پیام‌ها
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    # پاسخ پیش‌فرض متنی
    response = f"پاسخت 👇\n\n💬 {user_message} مربوط به مسائل حقوقی هست؟ اگر بله، لطفاً نوعش رو مشخص کن (مثل خانواده، قرارداد، کیفری و ...)"

    keyboard = [
        [InlineKeyboardButton("🔊 پخش صوتی همین پاسخ", callback_data=f"voice:{response}")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(response, reply_markup=reply_markup)

# تولید صوت از متن
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("voice:"):
        text = query.data.replace("voice:", "")
        tts = gTTS(text=text, lang="fa")
        tts.save("voice.mp3")
        await query.message.reply_voice(voice=open("voice.mp3", "rb"))
    elif query.data == "voice_mode":
        await query.message.reply_text("از این به بعد می‌تونی با دکمه «🔊 پخش صوتی» جواب‌هارو گوش بدی 🎧")

# هندلرها
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(button_handler))

# راه‌اندازی Webhook برای Render
async def main():
    port = int(os.environ.get("PORT", 8080))
    webhook_url = os.environ.get("RENDER_EXTERNAL_URL")

    if not webhook_url:
        raise ValueError("❌ آدرس RENDER_EXTERNAL_URL در Render تنظیم نشده است!")

    webhook_url = f"{webhook_url}/webhook"

    await app.bot.set_webhook(url=webhook_url)
    logger.info(f"✅ Webhook set to: {webhook_url}")

    # سرور همیشه روشن می‌مونه
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
