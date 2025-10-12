import os
import asyncio
from aiohttp import web
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from gtts import gTTS
import openai

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

async def ask_openai(prompt: str):
    completion = await openai.ChatCompletion.acreate(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message["content"]

def text_to_speech(text):
    tts = gTTS(text=text, lang='fa')
    file_path = "/tmp/voice.mp3"
    tts.save(file_path)
    return file_path

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [KeyboardButton("👩‍❤️‍👨 طلاق"), KeyboardButton("💰 مهریه")],
        [KeyboardButton("🏠 ارث"), KeyboardButton("📑 اجاره‌نامه")],
        [KeyboardButton("⚖️ سایر سوالات حقوقی")]
    ]
    markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text(
        "سلام 👋 خوش اومدی به ربات مشاور حقوقی محضرباشی.\n"
        "یکی از موضوعات زیر رو انتخاب کن یا سوالت رو بنویس 👇",
        reply_markup=markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    await update.message.reply_text("سؤالت دریافت شد ✅ لطفاً چند لحظه صبر کن...")

    answer = await ask_openai(f"پاسخ حقوقی ساده برای: {question}")
    await update.message.reply_text(answer)

    voice = text_to_speech(answer)
    await update.message.reply_voice(voice=open(voice, 'rb'))

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

async def index(request):
    return web.Response(text="✅ Mahzarbashi Bot is running")

async def run():
    runner = web.AppRunner(web.Application())
    runner.app.router.add_get("/", index)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", "10000")))
    await site.start()
    print("🚀 Bot is live on Render with Python 3.10!")

    await app.initialize()
    await app.start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(run())
