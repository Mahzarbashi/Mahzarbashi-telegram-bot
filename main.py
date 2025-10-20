import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import asyncio
import requests

# ---- متغیرهای محیطی ----
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ---- دستور start ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = (
        "🤖 خوش‌آمدید به ربات حقوقی محضرباشی!\n\n"
        "📚 این ربات پاسخگوی سؤالات عمومی حقوقی است.\n"
        "⚖️ در صورت نیاز به مشاوره تخصصی‌تر، به بخش «مشاوره با وکلای دادگستری» در سایت زیر مراجعه کنید:\n"
        "🌐 https://mahzarbashi.ir\n\n"
        "👩‍💼 سازنده: نسترن بنی‌طبا"
    )
    await update.message.reply_text(about_text)

# ---- پردازش سوالات حقوقی ----
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    if not user_text:
        return

    # --- بررسی محتوای حقوقی ---
    if any(word in user_text for word in ["طلاق", "مهریه", "نفقه", "چک", "قرارداد", "سند", "ملک", "دادگاه", "ارث"]):
        # پاسخ هوشمند
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "تو یک مشاور حقوقی با لحن دوستانه هستی."},
                {"role": "user", "content": user_text}
            ]
        }
        try:
            response = requests.post("https://api.openai.com/v1/chat/completions", json=data, headers=headers)
            reply = response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            reply = "متأسفم، مشکلی در ارتباط با سرور پیش آمد."

        await update.message.reply_text(reply)
        await update.message.reply_voice(voice="https://mahzarbashi.ir/static/audio/legal_response.mp3")  # نمونه صوتی
    else:
        await update.message.reply_text(
            "سؤال شما عمومی است. لطفاً پرسش را دقیق‌تر و در زمینه‌ی حقوقی مطرح کنید 🙏"
        )

# ---- راه‌اندازی ----
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🚀 Mahzarbashi Legal Assistant Bot is running ...")
    app.run_polling()
