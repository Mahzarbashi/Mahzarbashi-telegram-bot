import os
import json
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from gtts import gTTS
import openai

# 🔐 خواندن توکن‌ها از Environment Variables در Render
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN تعریف نشده است!")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY تعریف نشده است!")

openai.api_key = OPENAI_API_KEY


# 🎙️ تابع ساخت صدای پاسخ
async def generate_voice(text, filename="voice.mp3"):
    tts = gTTS(text=text, lang='fa')
    tts.save(filename)
    return filename


# 🚀 دستور start با دکمه‌های منو
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


# 🎛️ واکنش به کلیک روی دکمه‌ها
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

    await query.message.reply_text(text)
    voice_file = await generate_voice(text)
    await query.message.reply_voice(voice=open(voice_file, "rb"))


# 💬 پاسخ به سوالات آزاد کاربران
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    print(f"📨 پیام کاربر: {user_text}")

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "تو یک مشاور حقوقی رسمی سایت محضرباشی هستی."},
                {"role": "user", "content": user_text},
            ],
        )
        answer = response.choices[0].message["content"]
        await update.message.reply_text(answer)
        voice_file = await generate_voice(answer)
        await update.message.reply_voice(voice=open(voice_file, "rb"))
    except Exception as e:
        print("❌ خطا در ارتباط با OpenAI:", e)
        await update.message.reply_text("خطایی در پاسخگویی رخ داد، لطفاً دوباره تلاش کن.")


# 🌐 پاسخ به درخواست‌های وب (برای Render)
async def root(request):
    return web.Response(text="Mahzarbashi bot is running ✅")


# 🌐 مسیر دریافت پیام‌های تلگرام (POST)
async def webhook(request):
    data = await request.json()
    await app.update_queue.put(Update.de_json(data, app.bot))
    return web.Response(text="OK")


# ⚙️ ساخت اپ اصلی
app = Application.builder().token(TELEGRAM_TOKEN).build()

# 🧩 ثبت هندلرها
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# 🌍 تنظیم وب‌سرور aiohttp
web_app = web.Application()
web_app.add_routes([
    web.get("/", root),
    web.post("/", webhook)
])

if __name__ == "__main__":
    print("🚀 Mahzarbashi Bot started successfully on Render ✅")
    web.run_app(web_app, port=int(os.getenv("PORT", 8080)))
