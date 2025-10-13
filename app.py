import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, CallbackQueryHandler, filters
from gtts import gTTS
import openai
from aiohttp import web

# گرفتن توکن‌ها از محیط
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN تعریف نشده!")
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY تعریف نشده!")

openai.api_key = OPENAI_API_KEY

# تولید فایل صوتی
async def generate_voice(text, filename="voice.mp3"):
    tts = gTTS(text=text, lang='fa')
    tts.save(filename)
    return filename

# فرمان استارت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👩‍⚖️ طلاق", callback_data="divorce")],
        [InlineKeyboardButton("💍 مهریه", callback_data="mehrieh")],
        [InlineKeyboardButton("🏠 ارث و وصیت", callback_data="inheritance")],
        [InlineKeyboardButton("📞 مشاوره با وکیل", url="https://www.mahzarbashi.ir")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "سلام 👋\nبه ربات حقوقی محضرباشی خوش اومدی.\nموضوع مورد نظرت رو انتخاب کن:",
        reply_markup=reply_markup
    )

# پاسخ به دکمه‌ها
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "divorce":
        text = "طلاق توافقی راحت‌تر و سریع‌تر انجام میشه. می‌خوای مراحلش رو بگم؟"
    elif data == "mehrieh":
        text = "مهریه بر اساس نرخ روز محاسبه میشه. بگم چطور؟"
    elif data == "inheritance":
        text = "در ارث، نسبت خانوادگی تعیین‌کننده است. برات توضیح بدم؟"
    else:
        text = "برای اطلاعات بیشتر وارد سایت شو: https://www.mahzarbashi.ir"

    voice = await generate_voice(text)
    await query.message.reply_text(text)
    await query.message.reply_voice(voice=open(voice, "rb"))

# پاسخ به پیام‌های کاربر
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    response = await openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "تو یک مشاور حقوقی رسمی و حرفه‌ای سایت محضرباشی هستی."},
            {"role": "user", "content": user_text}
        ]
    )
    answer = response.choices[0].message.content
    await update.message.reply_text(answer)
    voice = await generate_voice(answer)
    await update.message.reply_voice(voice=open(voice, "rb"))

# وب‌هوک تست
async def webhook_root(request):
    return web.Response(text="✅ Mahzarbashi bot is active.")

# ساخت برنامه تلگرام
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ساخت سرور وب برای Render
web_app = web.Application()
web_app.add_routes([web.get("/", webhook_root)])

# اجرا
if __name__ == "__main__":
    web.run_app(web_app, port=int(os.getenv("PORT", 8080)))
