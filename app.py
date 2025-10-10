import os
from flask import Flask, request
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import openai
from gtts import gTTS

# ---- تنظیم کلیدها ----
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise ValueError("❌ TELEGRAM_TOKEN یا OPENAI_API_KEY پیدا نشد. لطفاً Environment Variables را در Render چک کنید.")

openai.api_key = OPENAI_API_KEY
bot = Bot(token=TELEGRAM_TOKEN)
app = Flask(__name__)

# ---- ایجاد Application ----
application = Application.builder().token(TELEGRAM_TOKEN).build()

# ---- دستور /start ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👩‍⚖️ مهریه", callback_data="faq_mehrieh")],
        [InlineKeyboardButton("💔 طلاق", callback_data="faq_talagh")],
        [InlineKeyboardButton("🏠 اجاره‌نامه", callback_data="faq_ejare")],
        [InlineKeyboardButton("💳 چک", callback_data="faq_cheque")],
        [InlineKeyboardButton("🌐 سایت محضرباشی", url="https://www.mahzarbashi.ir")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "سلام! 👋\nمن ربات *محضرباشی* هستم.\n"
        "می‌تونی یکی از موضوعات رایج زیر رو انتخاب کنی یا سوالت رو مستقیم بپرسی:",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# ---- پاسخ به کلیک روی دکمه‌ها ----
async def faq_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "faq_mehrieh":
        reply_text = "📌 *مهریه*: زن هر زمان بخواهد می‌تواند مهریه‌اش را مطالبه کند. اجرای مهریه از طریق دادگاه یا اجرای ثبت امکان‌پذیر است."
    elif query.data == "faq_talagh":
        reply_text = "📌 *طلاق*: برای طلاق توافقی نیاز به حضور زوجین در دادگاه و توافق بر سر مهریه، حضانت و جهیزیه وجود دارد."
    elif query.data == "faq_ejare":
        reply_text = "📌 *اجاره‌نامه*: قرارداد اجاره باید کتبی و با ذکر مدت و مبلغ تنظیم شود. در غیر این صورت مشکلات حقوقی پیش می‌آید."
    elif query.data == "faq_cheque":
        reply_text = "📌 *چک*: در صورت برگشت چک، دارنده می‌تواند گواهی عدم پرداخت گرفته و از طریق دادگاه یا اجرای ثبت اقدام کند."
    else:
        reply_text = "لطفاً برای اطلاعات بیشتر به سایت مراجعه کنید: www.mahzarbashi.ir"

    # ارسال متن
    await query.message.reply_text(reply_text, parse_mode="Markdown")

    # ارسال ویس
    tts = gTTS(text=reply_text, lang='fa')
    audio_path = f"voice_{query.id}.mp3"
    tts.save(audio_path)
    with open(audio_path, 'rb') as audio_file:
        await query.message.reply_voice(audio_file)
    os.remove(audio_path)

# ---- پاسخ به پیام‌های کاربر ----
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    # اگر سوال تخصصی باشد → هدایت به سایت
    if len(user_text) > 200 or any(word in user_text.lower() for word in ["قانون", "حقوق", "وکالت"]):
        reply_text = "سوال شما تخصصی است. لطفاً برای پاسخ کامل به سایت مراجعه کنید: www.mahzarbashi.ir"
    else:
        # پاسخ هوش مصنوعی
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_text}],
            max_tokens=300
        )
        reply_text = response['choices'][0]['message']['content']

    await update.message.reply_text(reply_text)

    # ارسال ویس
    tts = gTTS(text=reply_text, lang='fa')
    audio_path = f"voice_{update.message.message_id}.mp3"
    tts.save(audio_path)
    with open(audio_path, 'rb') as audio_file:
        await update.message.reply_voice(audio_file)
    os.remove(audio_path)

# ---- افزودن هندلرها ----
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(faq_handler))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

# ---- وبهوک ----
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.run_update(update)
    return "OK"

@app.route("/")
def index():
    return "ربات محضرباشی فعال است ✅"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
