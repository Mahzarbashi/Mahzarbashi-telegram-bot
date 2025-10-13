import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from gtts import gTTS
import openai
from aiohttp import web

# محیط‌ها
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise ValueError("❌ TELEGRAM_TOKEN یا OPENAI_API_KEY تعریف نشده!")

openai.api_key = OPENAI_API_KEY

# تولید فایل صوتی
async def generate_voice(text, filename="voice.mp3"):
    tts = gTTS(text=text, lang="fa")
    tts.save(filename)
    return filename

# شروع ربات
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
        text = "طلاق ممکن است توافقی یا یک‌طرفه باشد. می‌خوای برات توضیح بدم چطور اقدام کنی؟"
    elif data == "mehrieh":
        text = "مهریه معمولاً به تعداد سکه تعیین میشه. می‌خوای نحوه محاسبه‌ش رو بدونی؟"
    elif data == "inheritance":
        text = "ارث بستگی به نسبت خانوادگی داره. می‌خوای دقیق‌تر بدونی سهم‌الارثت چقدره؟"
    else:
        text = "برای مشاوره بیشتر به سایت محضرباشی برو: https://www.mahzarbashi.ir"

    voice_path = await generate_voice(text)
    await query.message.reply_text(text)
    await query.message.reply_voice(voice=open(voice_path, "rb"))

# پاسخ به پیام‌های متنی
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    try:
        response = await openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "تو یک مشاور رسمی سایت حقوقی محضرباشی هستی."},
                {"role": "user", "content": question},
            ],
        )
        answer = response.choices[0].message.content
        await update.message.reply_text(answer)
        voice_path = await generate_voice(answer)
        await update.message.reply_voice(voice=open(voice_path, "rb"))
    except Exception as e:
        await update.message.reply_text("⚠️ خطایی رخ داد، لطفاً دوباره تلاش کن.")

# وب‌سرور
async def webhook(request):
    return web.Response(text="✅ Mahzarbashi bot is running successfully!")

# ساخت اپ
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# اجرای سرور
web_app = web.Application()
web_app.add_routes([web.get("/", webhook)])

if __name__ == "__main__":
    web.run_app(web_app, port=int(os.getenv("PORT", 8080)))
