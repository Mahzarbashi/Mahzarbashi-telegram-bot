import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import asyncio

# فعال‌سازی لاگ برای خطاها
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# دریافت توکن از محیط
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("❌ توکن تلگرام پیدا نشد! لطفاً TELEGRAM_TOKEN را در Render تنظیم کنید.")

# دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! 👋 به ربات محضرباشی خوش اومدی.\nهر سوال حقوقی داری بپرس تا راهنماییت کنم.")

# پاسخ به پیام‌های متنی
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.lower()
    if "طلاق" in user_message:
        reply = "برای طلاق، باید دادخواست در دفتر خدمات قضایی ثبت بشه. 👩‍⚖️"
    elif "مهریه" in user_message:
        reply = "برای مهریه، زن می‌تونه از طریق اجرای ثبت یا دادگاه خانواده اقدام کنه."
    elif "حضانت" in user_message:
        reply = "حضانت فرزند تا ۷ سالگی با مادره، بعد از اون با نظر دادگاه مشخص می‌شه."
    else:
        reply = "سوالت حقوقی‌تر بپرس تا دقیق‌تر راهنماییت کنم. ⚖️"
    await update.message.reply_text(reply)

# ساخت اپلیکیشن
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # اجرای بات
    await app.run_polling()

# اجرای ایمن برای Render
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "Cannot close a running event loop" in str(e):
            pass  # Render خودش event loop را مدیریت می‌کند
        else:
            raise
