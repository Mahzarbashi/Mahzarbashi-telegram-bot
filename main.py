import os
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from gtts import gTTS
import tempfile

# گرفتن توکن از محیط Render
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("❌ توکن تلگرام پیدا نشد! لطفاً در Render مقدار TELEGRAM_TOKEN را تنظیم کنید.")

bot = Bot(token=TOKEN)
app = Flask(__name__)

# ⚙️ پاسخ متنی صمیمی با دکمه صوتی
async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text.strip().lower()

    # پاسخ پیش‌فرض دوستانه ✨
    reply_text = f"😊 {update.effective_user.first_name} عزیز!\nمن ربات محضرباشی‌ام 🤖✨\nسؤالتو بپرس تا با لحن صمیمی راهنماییت کنم 💬"

    # دکمه‌ی «گوش دادن صوتی»
    keyboard = [[InlineKeyboardButton("🎧 گوش دادن صوتی", callback_data=f"voice:{reply_text}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(reply_text, reply_markup=reply_markup)

# 🎧 تولید و ارسال صدای پاسخ با gTTS
async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("voice:"):
        text = query.data.replace("voice:", "")
        tts = gTTS(text=text, lang='fa')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            await bot.send_audio(chat_id=query.message.chat_id, audio=open(tmp_file.name, 'rb'), title="پاسخ صوتی 🎧")

        await query.edit_message_text("✅ فایل صوتی برات فرستادم 🎵")

# 🧩 راه‌اندازی بات
application = Application.builder().token(TOKEN).build()
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
application.add_handler(CallbackQueryHandler(button_handler))

# 🌐 Flask route برای Webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "OK"

@app.route("/")
def home():
    return "🤖 Mahzarbashi Bot is running and happy! 💫"

if __name__ == "__main__":
    import asyncio
    from telegram import TelegramError

    async def set_webhook():
        url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
        try:
            await bot.set_webhook(url)
            print(f"✅ Webhook set to: {url}")
        except TelegramError as e:
            print(f"⚠️ Webhook error: {e}")

    asyncio.run(set_webhook())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
