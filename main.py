import os
import logging
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from gtts import gTTS
import tempfile
import requests

# فعال کردن لاگ برای بررسی
logging.basicConfig(level=logging.INFO)

# گرفتن متغیرها از محیط
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not TELEGRAM_TOKEN or not GROQ_API_KEY:
    raise ValueError("❌ لطفاً TELEGRAM_TOKEN و GROQ_API_KEY را در Environment Variables ست کنید.")

# تعریف ربات
bot = Bot(token=TELEGRAM_TOKEN)

ABOUT_TEXT = """
🤖 ربات مشاوره حقوقی «محضرباشی»
📚 پاسخگوی پرسش‌های عمومی حقوقی شماست.

👩‍💼 توسعه و طراحی توسط: نسترن بنی‌طبا  
🌐 mahzarbashi.ir
"""

# دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! 👋\nمن ربات حقوقی محضرباشی هستم. سوالت در زمینه حقوق رو بپرس تا راهنماییت کنم.")

# دستور /about
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(ABOUT_TEXT)

# پاسخ به سوالات
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = update.message.text.strip()

    # فقط سؤالات حقوقی
    keywords = ["طلاق", "مهریه", "قرارداد", "ملک", "ارث", "چک", "اجاره", "شکایت", "قانون", "دادگاه", "حق"]
    if not any(word in user_question for word in keywords):
        await update.message.reply_text("این سؤال حقوقی نیست. لطفاً سوالت در زمینه مسائل حقوقی بپرس 🌿")
        return

    # درخواست به GROQ (یا OpenAI API)
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "شما یک مشاور حقوقی هستید که به زبان فارسی پاسخ می‌دهید."},
            {"role": "user", "content": user_question}
        ],
        "temperature": 0.5,
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        answer = response.json()["choices"][0]["message"]["content"]

        # بررسی تخصصی بودن سؤال
        if "تخصصی" in answer or "نیاز به بررسی بیشتر" in answer or len(answer) > 400:
            answer += "\n\n📞 برای مشاوره تخصصی‌تر، به بخش مشاوره وکلا در سایت mahzarbashi.ir مراجعه کنید."

        # پاسخ متنی
        await update.message.reply_text(answer)

        # پاسخ صوتی
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            tts = gTTS(answer, lang="fa")
            tts.save(f.name)
            await update.message.reply_voice(voice=open(f.name, "rb"))

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("متأسفم، خطایی رخ داد. لطفاً دوباره تلاش کنید ❗")

# راه‌اندازی برنامه
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("about", about))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    print("🚀 Mahzarbashi Bot started successfully on Render ✅")
    app.run_polling()
