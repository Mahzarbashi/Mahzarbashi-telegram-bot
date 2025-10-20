import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# 🔹 متغیر محیطی Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# 🔹 دستور start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = (
        "🤖 خوش‌آمدید به ربات حقوقی محضرباشی!\n\n"
        "📚 این ربات پاسخگوی سؤالات عمومی حقوقی است.\n"
        "⚖️ در صورت نیاز به مشاوره تخصصی‌تر، به بخش «مشاوره با وکلای دادگستری» در سایت زیر مراجعه کنید:\n"
        "🌐 https://mahzarbashi.ir\n\n"
        "👩‍💼 سازنده: نسترن بنی‌طبا"
    )
    await update.message.reply_text(about_text)

# 🔹 پردازش پیام‌ها
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    if not user_text:
        return

    # فقط سؤالات حقوقی پاسخ داده می‌شوند
    if any(word in user_text for word in ["طلاق", "مهریه", "نفقه", "چک", "قرارداد", "سند", "ملک", "دادگاه", "ارث"]):
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": "تو یک مشاور حقوقی با لحن دوستانه و حرفه‌ای هستی."},
                {"role": "user", "content": user_text}
            ]
        }

        try:
            response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
            reply = response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            reply = "متأسفم، مشکلی در پاسخگویی به وجود آمد. لطفاً دوباره تلاش کنید."

        await update.message.reply_text(reply)
    else:
        await update.message.reply_text(
            "سؤال شما خارج از حوزه حقوقی است. لطفاً پرسش خود را دقیق‌تر و در زمینه‌ی حقوقی مطرح کنید 🙏"
        )

# 🔹 اجرای ربات
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🚀 Mahzarbashi Legal Assistant (Groq) is running ...")
    app.run_polling()
