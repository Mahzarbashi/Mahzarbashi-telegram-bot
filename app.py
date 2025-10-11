from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import openai
import os
from gtts import gTTS
import io

# --- تنظیمات محیط ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # مثل https://mahzarbashi-telegram-bot.onrender.com/
PORT = int(os.environ.get("PORT", 8443))

openai.api_key = OPENAI_API_KEY

# --- دکمه‌ها ---
def get_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👰 مهریه", callback_data="مهریه"),
         InlineKeyboardButton("💔 طلاق", callback_data="طلاق")],
        [InlineKeyboardButton("🏠 اجاره و املاک", callback_data="املاک"),
         InlineKeyboardButton("⚖️ وصیت و ارث", callback_data="ارث")],
        [InlineKeyboardButton("📄 قراردادها", callback_data="قرارداد"),
         InlineKeyboardButton("🚔 جرایم و تخلفات", callback_data="جرایم")],
        [InlineKeyboardButton("🏢 ثبت شرکت", callback_data="شرکت"),
         InlineKeyboardButton("🔹 سایر موارد", callback_data="سایر")]
    ])

# --- شروع ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 👋 من دستیار حقوقی محضرباشی هستم.\n"
        "سؤالت رو بپرس یا یکی از موضوعات زیر رو انتخاب کن 👇",
        reply_markup=get_keyboard()
    )

# --- دکمه‌ها ---
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(f"شما موضوع «{query.data}» را انتخاب کردید. حالا سوال خودت رو بنویس 🌸")

# --- تشخیص سوال تخصصی ---
def is_advanced_question(text):
    advanced = ["ماده", "پرونده", "دادگاه", "وکالت", "دادسرا", "قانون"]
    return any(word in text for word in advanced)

# --- پاسخ ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if is_advanced_question(text):
        await update.message.reply_text(
            "❗ سؤال شما نیاز به بررسی دقیق دارد.\n"
            "برای مشاوره تخصصی وارد سایت شوید 👇\n"
            "🌐 [mahzarbashi.ir](https://mahzarbashi.ir)",
            parse_mode="Markdown"
        )
        return

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "تو یک مشاور حقوقی حرفه‌ای و صمیمی هستی که پاسخ‌های دقیق و قابل فهم می‌نویسد."},
            {"role": "user", "content": text}
        ]
    )
    answer = response.choices[0].message.content

    await update.message.reply_text(answer)

    tts = gTTS(answer, lang="fa")
    audio = io.BytesIO()
    tts.write_to_fp(audio)
    audio.seek(0)
    await update.message.reply_voice(voice=audio)

# --- اپلیکیشن ---
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- Webhook ---
if __name__ == "__main__":
    print("🚀 Starting webhook on Render...")
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TELEGRAM_TOKEN,
        webhook_url=f"{WEBHOOK_URL}{TELEGRAM_TOKEN}"
    )
