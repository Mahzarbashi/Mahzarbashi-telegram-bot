import os
import logging
import asyncio
import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# فعال‌سازی log برای خطاها
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# --- توکن تلگرام ---
TOKEN = os.getenv("TELEGRAM_TOKEN", "8249435097:AAGOIS7GfwBayCTSZGFahbMhYcZDFxzSGAg")
if not TOKEN:
    raise ValueError("❌ توکن تلگرام پیدا نشد! لطفاً TELEGRAM_TOKEN را در Render تنظیم کنید.")

# --- معرفی اولیه ---
INTRO_TEXT = (
    "👋 سلام! من ربات رسمی *محضرباشی* هستم.\n"
    "توسعه‌دهنده‌ی من *نسترن بنی‌طبا* است.\n\n"
    "من به سؤالات حقوقی شما پاسخ متنی و صوتی می‌دهم. "
    "اگر پرسشت خیلی تخصصی باشد، شما را به سایت رسمی [محضرباشی](https://mahzarbashi.ir) راهنمایی می‌کنم."
)

# --- پاسخ به دستور /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(INTRO_TEXT, parse_mode="Markdown")

# --- تابع پاسخ به پیام‌ها ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    # بررسی اینکه سؤال حقوقی هست یا نه
    if any(keyword in text for keyword in ["طلاق", "مهریه", "اجاره", "وصیت", "شکایت", "دادگاه", "قرارداد", "ارث", "حضانت", "جرم", "قانون"]):
        # پاسخ حقوقی نمونه (۵ تا ۷ سطر)
        answer = (
            "پرسش شما مرتبط با موضوعات حقوقی است ✅\n\n"
            "در چنین مواردی، بر اساس قانون مدنی و آیین دادرسی، "
            "باید توجه داشت که پاسخ دقیق بسته به شرایط پرونده و مدارک موجود متفاوت است.\n\n"
            "به‌صورت کلی، قانون در این مورد چارچوب مشخصی دارد که باید با مدارک اثباتی بررسی شود.\n\n"
            "برای مطالعه‌ی کامل‌تر یا دریافت مشاوره‌ی تخصصی‌تر، "
            "به بخش مشاوره در سایت [محضرباشی](https://mahzarbashi.ir) مراجعه کنید."
        )
        await update.message.reply_text(answer, parse_mode="Markdown")

        # ایجاد پاسخ صوتی (در آینده قابل اضافه‌کردن با gTTS)
    else:
        await update.message.reply_text(
            "❗ این سؤال در حوزه‌ی حقوقی نیست.\n"
            "لطفاً پرسش خود را درباره‌ی قانون، قرارداد، مهریه، طلاق، ارث یا دادگاه مطرح کنید."
        )

# --- ساخت اپلیکیشن ---
application = ApplicationBuilder().token(TOKEN).build()

# --- هندلرها ---
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- اجرای وبهوک در Render ---
nest_asyncio.apply()

async def main():
    print("🚀 Starting Mahzarbashi Telegram Bot...")

    render_url = os.getenv("RENDER_EXTERNAL_URL")
    if not render_url:
        raise ValueError("❌ مقدار RENDER_EXTERNAL_URL در Render تنظیم نشده است.")

    webhook_url = f"{render_url}/{TOKEN}"

    await application.initialize()
    await application.start()
    await application.bot.set_webhook(webhook_url)
    print(f"✅ Webhook set to: {webhook_url}")

    await application.updater.start_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        url_path=TOKEN,
        webhook_url=webhook_url
    )

    print("💡 Bot is now running and listening for messages.")
    await application.updater.idle()

if __name__ == "__main__":
    asyncio.run(main())
