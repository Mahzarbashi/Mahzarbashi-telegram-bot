import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, CallbackQueryHandler, filters
from gtts import gTTS
import openai
from aiohttp import web

# توکن‌ها از متغیرهای محیطی Render
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

# پاسخ صوتی
async def generate_voice(text, filename="voice.mp3"):
    tts = gTTS(text=text, lang='fa')
    tts.save(filename)
    return filename

# شروع ربات با دکمه‌ها
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👩‍⚖️ طلاق", callback_data="divorce")],
        [InlineKeyboardButton("💍 مهریه", callback_data="mehrieh")],
        [InlineKeyboardButton("🏠 ارث و وصیت", callback_data="inheritance")],
        [InlineKeyboardButton("📞 مشاوره با وکیل", url="https://www.mahzarbashi.ir")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "سلام 👋\nبه ربات حقوقی محضرباشی خوش اومدی.\nلطفاً موضوع مورد نظرت رو انتخاب کن:",
        reply_markup=reply_markup,
    )

# واکنش به دکمه‌ها
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    topic = query.data
    if topic == "divorce":
        text = "برای طلاق، نوع طلاق (توافقی یا یک‌طرفه) مهمه. می‌خوای برات توضیح بدم چطور اقدام کنی؟"
    elif topic == "mehrieh":
        text = "مهریه بر اساس مبلغ یا تعداد سکه تعیین میشه. دوست داری نحوه محاسبه مهریه رو بدونی؟"
    elif topic == "inheritance":
        text = "در موضوع ارث، نسبت خانوادگی تعیین‌کننده است. می‌خوای بر اساس نسبتت راهنمایی‌ات کنم؟"
    else:
        text = "برای مشاوره بیشتر وارد سایت شو: https://www.mahzarbashi.ir"

    voice_file = await generate_voice(text)
    await query.message.reply_text(text)
    await query.message.reply_voice(voice=open(voice_file, "rb"))

# واکنش به سوالات آزاد کاربران
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        response = await openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "تو یک مشاور حقوقی رسمی سایت محضرباشی هستی."},
                {"role": "user", "content": user_text},
            ],
        )
        answer = response.choices[0].message.content
        await update.message.reply_text(answer)
        voice_file = await generate_voice(answer)
        await update.message.reply_voice(voice=open(voice_file, "rb"))
    except Exception as e:
        await update.message.reply_text("خطایی رخ داد، لطفاً دوباره تلاش کن.")

# وب‌سرور برای Render
async def webhook(request):
    return web.Response(text="Mahzarbashi bot is running ✅")

# ساخت اپلیکیشن
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

web_app = web.Application()
web_app.add_routes([web.get("/", webhook)])

if __name__ == "__main__":
    web.run_app(web_app, port=int(os.getenv("PORT", 8080)))
