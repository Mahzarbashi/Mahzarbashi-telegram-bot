import os
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    MessageHandler, 
    ContextTypes, 
    filters
)

# -----------------------------
# تنظیمات اولیه
# -----------------------------
TOKEN = os.environ.get("TELEGRAM_TOKEN", "8249435097:AAGOIS7GfwBayCTSZGFahbMhYcZDFxzSGAg")
WEBHOOK_URL = f"https://mahzarbashi-telegram-bot-1-usa9.onrender.com/{TOKEN}"

# -----------------------------
# دستورات ربات
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌸 سلام! من ربات حقوقی محضرباشی هستم.\n"
        "این ربات توسط *نسترن بنی‌طبا* ساخته شده و پاسخگوی سؤالات حقوقی شماست.\n"
        "سؤالت رو بنویس تا بررسی کنم ⚖️",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if "طلاق" in text:
        reply = (
            "در موضوع طلاق، معمولاً باید دادخواست از طریق دفاتر خدمات قضایی ثبت شود. "
            "در صورتی که زن قصد طلاق داشته باشد، باید یکی از شروط ضمن عقد یا دلایل موجه را ارائه دهد. "
            "برای جزئیات بیشتر می‌تونی به بخش مشاوره سایت محضرباشی سر بزنی 🌐"
        )
    elif "مهریه" in text:
        reply = (
            "مهریه حق قانونی زن است و هر زمان بخواهد می‌تواند آن را مطالبه کند. "
            "اگر مهریه عندالاستطاعه باشد، مرد باید توان مالی خود را ثابت کند. "
            "در غیر این صورت دادگاه دستور اجرای مهریه را صادر می‌کند ⚖️"
        )
    elif "اجاره" in text or "مستأجر" in text:
        reply = (
            "در قرارداد اجاره، مستأجر موظف است ملک را در زمان مشخص تخلیه کند و موجر هم باید مبلغ رهن را بازگرداند. "
            "برای اختلافات مربوط به تمدید یا تخلیه، شورای حل اختلاف صلاحیت رسیدگی دارد. "
            "جزئیات بیشتر در سایت محضرباشی موجود است 🏠"
        )
    else:
        reply = (
            "سؤال شما بررسی شد اما نیاز به توضیح بیشتری دارد. "
            "لطفاً موضوع را دقیق‌تر بنویس یا از طریق سایت محضرباشی برای مشاوره تخصصی اقدام کن 🌐"
        )

    await update.message.reply_text(reply)

# -----------------------------
# اجرای ربات
# -----------------------------
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", "10000")),
        url_path=TOKEN,
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    asyncio.run(main())
