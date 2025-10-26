import os
import tempfile
import asyncio
import nest_asyncio
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
from gtts import gTTS
from flask import Flask, request

# فعال‌سازی nest_asyncio برای Render
nest_asyncio.apply()

# -----------------------------
# تنظیمات اولیه
# -----------------------------
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("❌ توکن تلگرام پیدا نشد! لطفاً TELEGRAM_TOKEN را در Render تنظیم کنید.")

bot = Bot(token=TOKEN)
app = Flask(__name__)

# -----------------------------
# معرفی ربات
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    intro_text = (
        "👋 سلام!\n"
        "من ربات رسمی حقوقی «محضرباشی» هستم 🤖\n"
        "این ربات توسط **نسترن بنی‌طبا** ساخته شده 💼\n"
        "می‌تونم به سؤالات حقوقی شما پاسخ بدم، هم متنی هم صوتی 🎧\n\n"
        "سؤالتو بپرس تا راهنماییت کنم ✨"
    )
    await update.message.reply_text(intro_text, parse_mode="Markdown")

# -----------------------------
# پاسخ به پیام‌ها
# -----------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    keywords = [
        "طلاق", "مهریه", "وصیت", "شکایت", "قرارداد",
        "دادگاه", "حقوق", "کیفری", "دیوان", "نفقه", "اجاره"
    ]

    if not any(k in text for k in keywords):
        await update.message.reply_text(
            "❗ من فقط به سؤالات **حقوقی** پاسخ می‌دم. "
            "لطفاً پرسشت رو در زمینه حقوقی مطرح کن ⚖️", parse_mode="Markdown"
        )
        return

    # پاسخ نمونه ۵ تا ۷ سطر
    reply_text = (
        "⚖️ پاسخ حقوقی:\n"
        "در این موضوع، طبق قانون مدنی و آیین دادرسی، هر پرونده با توجه به مدارک و شرایط طرفین بررسی می‌شود. "
        "برخی تصمیمات نیاز به مراجعه به دادگاه و ارائه شواهد دارند. "
        "در موضوع قرارداد یا مهریه، قوانین خاص اجرا می‌شود و می‌توان اقدامات قانونی انجام داد. "
        "برای جزئیات بیشتر و مشاوره تخصصی، به سایت [محضرباشی](https://mahzarbashi.ir) مراجعه کنید 🌐"
    )

    # دکمه‌ی پخش صوتی
    keyboard = [[InlineKeyboardButton("🎧 گوش دادن صوتی", callback_data=f"voice:{reply_text}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(reply_text, reply_markup=reply_markup)

# -----------------------------
# تولید صوت
# -----------------------------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("voice:"):
        text = query.data.replace("voice:", "")
        tts = gTTS(text=text, lang="fa")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            await bot.send_audio(
                chat_id=query.message.chat_id,
                audio=open(tmp_file.name, "rb"),
                title="پاسخ صوتی 🎧"
            )
        await query.edit_message_text("✅ فایل صوتی ارسال شد 🎵")

# -----------------------------
# ساخت اپلیکیشن
# -----------------------------
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
application.add_handler(CallbackQueryHandler(button_handler))

# -----------------------------
# مسیرهای Flask
# -----------------------------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "OK"

@app.route("/")
def home():
    return "🤖 Mahzarbashi Bot is running successfully!"

# -----------------------------
# اجرای Webhook در Render
# -----------------------------
async def main():
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    if not render_url:
        raise ValueError("❌ RENDER_EXTERNAL_URL در Render تنظیم نشده است.")

    webhook_url = f"{render_url}/{TOKEN}"
    print(f"🚀 Starting Mahzarbashi Bot... Webhook: {webhook_url}")

    await application.initialize()
    await application.start()
    await bot.set_webhook(webhook_url)
    print("✅ Webhook set successfully!")

    await application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        url_path=TOKEN,
        webhook_url=webhook_url,
    )

# -----------------------------
# شروع اصلی
# -----------------------------
if __name__ == "__main__":
    asyncio.run(main())
