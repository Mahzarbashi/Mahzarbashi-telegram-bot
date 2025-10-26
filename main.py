import os
import tempfile
import asyncio
import nest_asyncio
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters, CallbackQueryHandler
from gtts import gTTS

nest_asyncio.apply()

# 🔑 توکن از محیط Render
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("❌ توکن تلگرام پیدا نشد! لطفاً TELEGRAM_TOKEN را در Render تنظیم کنید.")

bot = Bot(token=TOKEN)
app = Flask(__name__)

# 🌐 معرفی نسترن بنی‌طبا در شروع
async def start(update: Update, context: CallbackContext):
    intro_text = (
        "سلام 👋\n"
        "من ربات هوشمند «محضرباشی» هستم 🤖\n"
        "این ربات توسط **نسترن بنی‌طبا** طراحی و توسعه داده شده 💼\n"
        "من اینجام تا به سؤالات حقوقی شما پاسخ بدم — هم به‌صورت متنی هم صوتی 🎧\n\n"
        "سؤالتو بفرست تا راهنماییت کنم ✨"
    )
    await update.message.reply_text(intro_text)

# ⚖️ پاسخ به سؤالات حقوقی
async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text.strip().lower()

    # بررسی اینکه سوال حقوقی هست یا نه
    keywords = ["طلاق", "مهریه", "وصیت", "شکایت", "قرارداد", "محکمه", "دادگاه", "حقوق", "کیفری", "دیوان", "نفقه", "اجاره"]
    if not any(k in text for k in keywords):
        await update.message.reply_text(
            "📘 من فقط به سؤالات **حقوقی** پاسخ می‌دم. لطفاً سؤال خودت رو در زمینه حقوق بپرس ⚖️"
        )
        return

    # پاسخ نمونه‌ی حقوقی
    reply_text = (
        "⚖️ پاسخ حقوقی:\n"
        "در این مورد باید توجه داشت که هر پرونده با شرایط خاص خودش بررسی می‌شود. "
        "طبق قانون مدنی و آیین دادرسی، تصمیم نهایی بستگی به مدارک، شواهد و اظهارات طرفین دارد. "
        "اگر موضوع شامل قرارداد یا شکایت رسمی است، باید متن دقیق مدارک بررسی شود. "
        "برای جزئیات بیشتر و دریافت مشاوره تخصصی، می‌توانید به سایت محضرباشی مراجعه کنید 🌐\n"
        "👉 mahzarbashi.ir"
    )

    # دکمه‌ی پخش صوت
    keyboard = [[InlineKeyboardButton("🎧 گوش دادن صوتی", callback_data=f"voice:{reply_text}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(reply_text, reply_markup=reply_markup)

# 🎧 تبدیل پاسخ به صوت
async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("voice:"):
        text = query.data.replace("voice:", "")
        tts = gTTS(text=text, lang='fa')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            await bot.send_audio(chat_id=query.message.chat_id, audio=open(tmp_file.name, 'rb'), title="پاسخ صوتی 🎧")

        await query.edit_message_text("✅ فایل صوتی ارسال شد 🎵")

# 🔧 تنظیم هندلرها
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
application.add_handler(CallbackQueryHandler(button_handler))

# 🌍 مسیرهای Flask
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "OK"

@app.route("/")
def home():
    return "🤖 Mahzarbashi Bot is running successfully!"

# 🚀 اجرای Webhook در Render
if __name__ == "__main__":
    async def main():
        print("🚀 Mahzarbashi Bot is starting...")
        await application.initialize()
        await application.start()
        print("✅ Webhook running successfully!")

        await application.run_webhook(
            listen="0.0.0.0",
            port=int(os.environ.get("PORT", 8080)),
            url_path=TOKEN,
            webhook_url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}",
        )

    asyncio.run(main())
