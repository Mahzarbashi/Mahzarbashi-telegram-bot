import os
import json
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from gtts import gTTS
import openai

# 🧩 متغیرهای محیطی
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise ValueError("❌ TELEGRAM_TOKEN یا OPENAI_API_KEY تعریف نشده است!")

openai.api_key = OPENAI_API_KEY

# 🎤 تبدیل متن به صدا
async def generate_voice(text, filename="voice.mp3"):
    tts = gTTS(text=text, lang='fa')
    tts.save(filename)
    return filename

# 🎛️ دکمه شروع
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

# 🎛️ دکمه‌ها
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    topic = query.data
    if topic == "divorce":
        text = "در مورد طلاق، نوع طلاق (توافقی یا یک‌طرفه) اهمیت داره. دوست داری راهکار قانونی‌اش رو بدونی؟"
    elif topic == "mehrieh":
        text = "مهریه بر اساس مبلغ یا تعداد سکه محاسبه میشه. می‌خوای نحوه محاسبه مهریه‌ات رو بگم؟"
    elif topic == "inheritance":
        text = "در بحث ارث، نسبت خانوادگی تعیین‌کننده است. می‌خوای بدونی چه سهمی داری؟"
    else:
        text = "برای مشاوره بیشتر، وارد سایت شو: https://www.mahzarbashi.ir"

    voice_file = await generate_voice(text)
    await query.message.reply_text(text)
    await query.message.reply_voice(voice=open(voice_file, "rb"))

# 💬 پاسخ به پیام کاربران
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    print(f"📨 کاربر نوشت: {user_text}")

    try:
        response = await openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "تو یک مشاور حقوقی رسمی و مودب سایت محضرباشی هستی."},
                {"role": "user", "content": user_text},
            ],
        )
        answer = response.choices[0].message.content
        await update.message.reply_text(answer)
        voice_file = await generate_voice(answer)
        await update.message.reply_voice(voice=open(voice_file, "rb"))
    except Exception as e:
        print("❌ خطا در پاسخ OpenAI:", e)
        await update.message.reply_text("خطایی رخ داد، لطفاً دوباره تلاش کن.")

# ✅ مسیر اصلی برای تست Render
async def root(request):
    return web.Response(text="✅ Mahzarbashi bot is running successfully!")

# ✅ دریافت پیام از Telegram
async def webhook(request):
    try:
        data = await request.json()
        print("📩 دریافت از Telegram:", json.dumps(data, ensure_ascii=False, indent=2))
        update = Update.de_json(data, app.bot)
        await app.process_update(update)
    except Exception as e:
        print("❌ خطا در پردازش پیام:", e)
    return web.Response(text="ok")

# ⚙️ ساخت اپ تلگرام
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# 🌐 ساخت وب‌سرور aiohttp
web_app = web.Application()
web_app.add_routes([
    web.get("/", root),
    web.post("/", webhook)
])

if __name__ == "__main__":
    print("🚀 Mahzarbashi Bot started successfully on Render ✅")
    web.run_app(web_app, port=int(os.getenv("PORT", 10000)))
