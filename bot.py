import os
import logging
from fastapi import FastAPI, Request
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import openai

# ----------------- تنظیمات -----------------
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")  # توکن ربات تلگرام
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  # کلید OpenAI
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")      # لینک Webhook Render

openai.api_key = OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
app = FastAPI()

# ----------------- توابع ربات -----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("سوالات رایج", callback_data='faq')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "سلام! من ربات حقوقی محضرباشی هستم. سوالت رو بپرس.", 
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    # تماس با OpenAI GPT
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"پرسش حقوقی: {user_text}"}],
            temperature=0.2
        )
        answer = response.choices[0].message.content

        # بررسی تخصصی بودن سوال (مثال ساده)
        if "مشاوره" in answer or "وکالت" in answer:
            answer += "\n\nبرای مشاوره تخصصی با وکیل، لطفاً به این لینک مراجعه کنید: https://mahzarbashi.ir/consult"

        await update.message.reply_text(answer)
    except Exception as e:
        logging.error(e)
        await update.message.reply_text("متأسفم، مشکلی پیش آمد. لطفاً دوباره امتحان کنید.")

# ----------------- هَندلِرها -----------------
app_telegram = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

# ----------------- Webhook FastAPI -----------------
@app.post(f"/webhook/{TELEGRAM_TOKEN}")
async def telegram_webhook(request: Request):
    update = Update.de_json(await request.json(), bot)
    await app_telegram.update_queue.put(update)
    return {"ok": True}

# ----------------- Route تست -----------------
@app.get("/")
def root():
    return {"message": "ربات محضرباشی فعال است!"}
