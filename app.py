import os
from aiohttp import web
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from gtts import gTTS
import openai
import asyncio

# 🔑 گرفتن توکن‌ها از تنظیمات Render
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

# 🎯 پاسخ از ChatGPT
async def ask_openai(prompt: str):
    response = await openai.ChatCompletion.acreate(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message["content"]

# 🎤 تبدیل پاسخ به صوت
def text_to_speech(text):
    tts = gTTS(text=text, lang='fa')
    path = "/tmp/voice.mp3"
    tts.save(path)
    return path

# 🚀 دکمه‌های اصلی
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [KeyboardButton("👩‍❤️‍👨 طلاق"), KeyboardButton("💰 مهریه")],
        [KeyboardButton("🏠 ارث"), KeyboardButton("📑 اجاره‌نامه")],
        [KeyboardButton("⚖️ سایر سوالات حقوقی")]
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text(
        "سلام 👋 خوش اومدی به ربات مشاور حقوقی محضرباشی.\n"
        "یکی از موضوعات زیر رو انتخاب کن یا سوالت رو بنویس 👇",
        reply_markup=reply_markup
    )

# 💬 پاسخ به پیام‌ها
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text("سؤالت دریافت شد ✅ لطفاً چند لحظه صبر کن...")

    ai_text = await ask_openai(f"پاسخ حقوقی ساده برای: {user_text}")
    await update.message.reply_text(ai_text)

    voice_path = text_to_speech(ai_text)
    await update.message.reply_voice(voice=open(voice_path, 'rb'))

# ⚙️ ساخت ربات
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# 🌐 وب‌سرور برای Render
async def index(request):
    return web.Response(text="✅ Mahzarbashi Assistant is running")

async def run():
    runner = web.AppRunner(web.Application())
    runner.app.router.add_get("/", index)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", "10000")))
    await site.start()
    print("🚀 Bot is live on Render!")

    await app.initialize()
    await app.start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(run())
