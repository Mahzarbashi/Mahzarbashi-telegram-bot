import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from gtts import gTTS
from io import BytesIO
import openai

# دریافت توکن‌ها از Environment Variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN پیدا نشد. لطفاً Environment Variables را تنظیم کنید.")
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY پیدا نشد. لطفاً Environment Variables را تنظیم کنید.")

openai.api_key = OPENAI_API_KEY

# دستور start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "سلام! من ربات محضرباشی هستم 🤖\n"
        "می‌تونی از من سوالات حقوقی بپرسی.\n\n"
        "برای اطلاعات بیشتر دستور /about را بزن."
    )
    await update.message.reply_text(text)

# دستور about
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "ربات مشاور حقوقی سایت محضرباشی\n"
        "وبسایت: www.mahzarbashi.ir\n"
        "این ربات توسط نسترن بنی طبا ساخته شده است."
    )
    await update.message.reply_text(text)

# بررسی متن و پاسخ با GPT
async def gpt_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    
    # اگر متن خیلی تخصصی بود به سایت هدایت شود
    keywords_special = ["مهریه", "طلاق", "چک", "قرارداد", "سند رسمی", "کلاهبرداری", "ارث"]
    if any(word in user_text for word in keywords_special):
        response_text = (
            "سوال شما کمی تخصصی است ⚖️\n"
            "می‌توانید پاسخ دقیق و کامل را در سایت محضرباشی بگیرید:\n"
            "www.mahzarbashi.ir\n\n"
            "همچنین امکان مشاوره تلفنی با وکیل پایه یک دادگستری هم وجود دارد."
        )
    else:
        # پاسخ GPT
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "تو یک مشاور حقوقی هستی. پاسخ‌ها را دوستانه، ساده و واضح بده و اگر سوال تخصصی بود به سایت ارجاع بده."},
                    {"role": "user", "content": user_text}
                ],
                temperature=0.7
            )
            response_text = completion.choices[0].message.content.strip()
        except Exception as e:
            response_text = "متاسفم، در حال حاضر پاسخ نمی‌توانم بدهم. لطفاً بعدا دوباره امتحان کنید."

    # ارسال متن
    await update.message.reply_text(response_text)

    # ارسال صوت
    tts = gTTS(response_text, lang='fa')
    audio = BytesIO()
    tts.write_to_fp(audio)
    audio.seek(0)
    await update.message.reply_voice(voice=audio)

# ساخت اپلیکیشن
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# هندلرها
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("about", about))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gpt_response))

# اجرای ربات
if __name__ == "__main__":
    print("🚀 Mahzarbashi Bot is running...")
    app.run_polling()
