import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

# فعال‌سازی لاگ‌ها
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# گرفتن توکن از محیط Render
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("❌ توکن تلگرام پیدا نشد! لطفاً TELEGRAM_TOKEN را در Render تنظیم کنید.")

# --- دستور شروع ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 👋 به ربات محضرباشی خوش اومدی.\n"
        "هر سوال حقوقی داری، بپرس تا راهنماییت کنم ⚖️"
    )

# --- پاسخ به پیام‌ها ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()

    if "طلاق" in text:
        answer = "برای طلاق باید دادخواست از طریق دفتر خدمات قضایی ثبت بشه 👩‍⚖️"
    elif "مهریه" in text:
        answer = "برای مهریه زن می‌تونه از طریق اجرای ثبت یا دادگاه خانواده اقدام کنه 💰"
    elif "حضانت" in text:
        answer = "حضانت فرزند تا ۷ سالگی با مادره، بعد از اون با نظر دادگاه مشخص میشه 👶"
    else:
        answer = "سوالت حقوقی‌تر بپرس تا دقیق‌تر راهنماییت کنم ⚖️"

    await update.message.reply_text(answer)

# --- اجرای اصلی ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # اجرای polling در حالت همزمان
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
