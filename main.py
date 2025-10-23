import os
import json
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# -----------------------------
# پیکربندی لاگ‌ها
# -----------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# -----------------------------
# دریافت کلیدها از Render
# -----------------------------
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# -----------------------------
# تابع ارتباط با مدل Groq (برای پاسخ هوشمند)
# -----------------------------
def ask_groq(prompt):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": "تو یک دستیار حقوقی صمیمی و حرفه‌ای هستی که لحن مهربان، قابل اعتماد و همراه با ایموجی دارد."},
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Groq error: {e}")
        return "متأسفم 😔 مشکلی در پاسخ‌دهی پیش اومده، لطفاً دوباره تلاش کن."

# -----------------------------
# دستور شروع ربات
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "سلام 👋 خوش اومدی به دستیار حقوقی *محضرباشی*\n\n"
        "من اینجام تا بهت کمک کنم پاسخ سؤالات حقوقی‌ت رو بدون استرس پیدا کنی ⚖️💬\n\n"
        "📚 می‌تونی بپرسی مثل:\n"
        "• مهریه به نرخ روز چطور محاسبه میشه؟\n"
        "• شرایط اجاره‌نامه چیه؟\n"
        "• دیه و مجازات‌ها چطور تعیین میشن؟\n\n"
        "👇 یکی از گزینه‌های زیر رو انتخاب کن یا سؤالت رو تایپ کن:"
    )

    keyboard = [
        [InlineKeyboardButton("💍 مهریه", callback_data="مهریه چیست؟")],
        [InlineKeyboardButton("🏠 اجاره‌نامه", callback_data="شرایط اجاره‌نامه")],
        [InlineKeyboardButton("⚖️ دیه و مجازات‌ها", callback_data="دیه و مجازات‌ها چگونه است؟")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=reply_markup)

# -----------------------------
# پاسخ به کلیک دکمه‌ها
# -----------------------------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    question = query.data
    reply = ask_groq(question)
    await query.message.reply_text(reply)

# -----------------------------
# پاسخ به پیام‌های متنی
# -----------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    reply = ask_groq(text)
    await update.message.reply_text(reply)

# -----------------------------
# اجرای اصلی برنامه
# -----------------------------
if __name__ == "__main__":
    if not BOT_TOKEN:
        raise ValueError("❌ توکن تلگرام پیدا نشد! لطفاً در Render مقدار TELEGRAM_BOT_TOKEN را تنظیم کنید.")
    if not GROQ_API_KEY:
        raise ValueError("❌ کلید Groq پیدا نشد! لطفاً در Render مقدار GROQ_API_KEY را تنظیم کنید.")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.ALL, handle_message))

    from telegram.ext import CallbackQueryHandler
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("🤖 Mahzarbashi Assistant is running on Render...")
    app.run_polling()
