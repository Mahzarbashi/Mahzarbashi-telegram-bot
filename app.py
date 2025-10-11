from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import openai
import os
from gtts import gTTS
import io

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# دکمه‌های موضوعی حقوقی
def get_keyboard():
    keyboard = [
        [InlineKeyboardButton("مهریه", callback_data="مهریه"),
         InlineKeyboardButton("طلاق", callback_data="طلاق")],
        [InlineKeyboardButton("اجاره و املاک", callback_data="املاک"),
         InlineKeyboardButton("وصیت و ارث", callback_data="ارث")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! 👋\nمن دستیار حقوقی محضرباشی هستم. سوالت رو بپرس یا یکی از موضوعات زیر رو انتخاب کن:",
        reply_markup=get_keyboard()
    )

# پاسخ به دکمه‌ها
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    topic = query.data
    await query.message.reply_text(f"شما موضوع «{topic}» را انتخاب کردید. لطفاً سوال خود را تایپ کنید:")

# بررسی سوال تخصصی
def is_advanced_question(user_message: str) -> bool:
    advanced_keywords = ["سازمان قضایی", "ماده قانونی", "پرونده", "دادگاه عالی", "ماده ۲۱۳"]
    return any(word in user_message for word in advanced_keywords)

# پاسخ به سوال کاربر
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    if is_advanced_question(user_message):
        reply_text = (
            "❗ سوال شما خیلی تخصصی است.\n"
            "می‌توانید به سایت محضرباشی مراجعه کنید و با وکیل پایه یک دادگستری مشاوره دقیق بگیرید:\n"
            "🌐 [mahzarbashi.ir](https://mahzarbashi.ir)"
        )
        await update.message.reply_text(reply_text, parse_mode="Markdown")
        return

    # پاسخ OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "تو یک مشاور حقوقی صمیمی و حرفه‌ای هستی."},
            {"role": "user", "content": user_message}
        ],
        max_tokens=400
    )
    answer_text = response.choices[0].message.content

    # ارسال متن
    await update.message.reply_text(answer_text)

    # تولید صوت در حافظه و ارسال مستقیم
    tts = gTTS(answer_text, lang="fa")
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    await update.message.reply_voice(voice=audio_fp)

# ساخت اپلیکیشن و هندلرها
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
