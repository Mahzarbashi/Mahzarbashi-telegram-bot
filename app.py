import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from gtts import gTTS
import openai

# ========================
# تنظیمات ربات
# ========================
BOT_TOKEN = "8249435097:AAF8PSgEXDVYWYBIXn_q45bHKID_aYDAtqw"
WEBHOOK_PATH = f"/{BOT_TOKEN}"

openai.api_key = os.environ.get("OPENAI_API_KEY")  # حتما در Render ست شود

FAQ = {
    "چگونه سند ملک بگیرم؟": "برای گرفتن سند ملک، باید مراحل A و B و C را طی کنید...",
    "هزینه ثبت قرارداد چقدر است؟": "هزینه ثبت قرارداد بستگی به نوع قرارداد دارد، معمولا بین X تا Y تومان است.",
    "نحوه انتقال مالکیت خودرو؟": "برای انتقال مالکیت خودرو، ابتدا مدارک شناسایی و سند خودرو را آماده کنید و به دفترخانه مراجعه نمایید."
}

# ========================
# فرمان /start
# ========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "سلام! من دستیار حقوقی محضرباشی هستم.\n"
        "می‌توانم به سوالات رایج حقوقی پاسخ بدهم.\n"
        "اگر سوال شما تخصصی باشد، به وبسایت محضرباشی هدایت خواهید شد.\n"
        "سوالت رو بپرسید:"
    )
    await update.message.reply_text(welcome_text)

# ========================
# استفاده از OpenAI برای پاسخ‌دهی
# ========================
async def get_ai_answer(question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "تو یک دستیار حقوقی هستی. سوالات ساده حقوقی را جواب بده. سوالات پیچیده را هدایت کن."},
                {"role": "user", "content": question}
            ],
            temperature=0.5,
            max_tokens=500
        )
        answer = response.choices[0].message.content.strip()
        return answer
    except Exception as e:
        return "متأسفم، پاسخ به سوال شما در حال حاضر امکان‌پذیر نیست."

# ========================
# پردازش پیام‌ها
# ========================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # اگر سوال در FAQ باشد
    if text in FAQ:
        answer = FAQ[text]
    else:
        # سوال به هوش مصنوعی داده می‌شود
        answer = await get_ai_answer(text)

        # اگر پاسخ حاوی پیام تخصصی بود، هدایت به سایت
        if any(keyword in answer for keyword in ["تخصصی", "پیچیده", "وکلا"]):
            answer = (
                "سوال شما نیاز به بررسی تخصصی دارد.\n"
                "لطفاً به وبسایت محضرباشی مراجعه کنید و با وکلای ما در تماس باشید:\n"
                "https://www.mahzarbashi.ir"
            )

    # ارسال متن
    await update.message.reply_text(answer)

    # ارسال فایل صوتی
    try:
        tts = gTTS(answer, lang="fa")
        audio_file = "answer.mp3"
        tts.save(audio_file)
        await update.message.reply_voice(voice=open(audio_file, "rb"))
        os.remove(audio_file)
    except Exception as e:
        pass  # اگر gTTS خطا داد، فقط متن ارسال می‌شود

# ========================
# ساخت Application
# ========================
application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ========================
# اجرای Webhook روی Render
# ========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=BOT_TOKEN,
        webhook_url=f"https://mahzarbashi-telegram-bot-2-fh68.onrender.com/{BOT_TOKEN}"
    )
