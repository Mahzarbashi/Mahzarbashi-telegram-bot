import os
import asyncio
import nest_asyncio
import tempfile
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    CallbackQueryHandler,
    filters,
)
from gtts import gTTS

# حل مشکل event loop در محیط‌هایی مثل Render
nest_asyncio.apply()

# تنظیمات از محیط
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("توکن تلگرام پیدا نشد. لطفاً TELEGRAM_TOKEN را در Environment Variables تنظیم کن.")

HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if not HOSTNAME:
    raise ValueError("RENDER_EXTERNAL_HOSTNAME پیدا نشد. این مقدار را در Render تنظیم کن.")

WEBHOOK_URL = f"https://{HOSTNAME}/{TOKEN}"

app = FastAPI()
application = Application.builder().token(TOKEN).build()

# --- توابع کمکی ---
async def send_voice(chat_id: int, text: str):
    """تولید و ارسال فایل صوتی با gTTS"""
    tts = gTTS(text=text, lang="fa")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tts.save(tmp.name)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as audio:
            await application.bot.send_voice(chat_id=chat_id, voice=audio)
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass

# --- هندلرها ---
async def start_handler(update: Update, context: CallbackContext):
    name = update.effective_user.first_name or "دوست"
    intro = (
        f"سلام {name} عزیز! 👋\n"
        "من ربات «محضرباشی» هستم — ساخته‌شده توسط نسترن بنی‌طبا.\n"
        "می‌تونی هر سؤال حقوقی که داری بپرسی؛ من هم با زبان دوستانه جواب می‌دم و فایل صوتی هم می‌فرستم 🎧\n\n"
        "سؤالتو اینجا بنویس تا راهنمایی‌ات کنم ✨"
    )
    await update.message.reply_text(intro)
    await send_voice(update.effective_chat.id, intro)

async def message_handler(update: Update, context: CallbackContext):
    text = (update.message.text or "").strip()
    lc = text.lower()

    # کلیدواژه‌های ساده برای تشخیص سؤالات حقوقی
    keywords = [
        "طلاق", "مهریه", "نفقه", "حضانت", "قرارداد",
        "اجاره", "وصیت", "شکایت", "دادگاه", "وکالت", "ارث"
    ]

    if not any(k in lc for k in keywords):
        reply = (
            "⚠️ من فقط به سؤالات حقوقی پاسخ می‌دم. لطفاً سوالت رو در مورد طلاق، مهریه، قرارداد، ارث یا امور دادگاه بپرس.\n\n"
            "برای مشاورهٔ کامل‌تر و منابع بیشتر به سایت محضرباشی سر بزن:\nhttps://mahzarbashi.ir"
        )
        await update.message.reply_text(reply)
        await send_voice(update.effective_chat.id, reply)
        return

    # پاسخ دوستانه (۵-۷ سطر تقریبی)
    reply = (
        "⚖️ پاسخ کوتاه حقوقی (دوستانه):\n"
        "در این موضوع معمولاً باید جزئیات پرونده و مدارک بررسی شود. "
        "قانون چارچوب کلی را مشخص کرده اما نتیجه وابسته به شرایط است.\n"
        "اگر مربوط به قرارداد یا مطالبهٔ مالی است، مدارک کتبی و رسیدها بسیار مهم‌اند. "
        "برای اقدام قانونی احتمالی معمولاً نیاز به ثبت شکایت یا مراجعه به دفتر خدمات قضایی هست.\n"
        "برای دریافت مشاورهٔ دقیق‌تر و بررسی مدارک، به بخش مشاورهٔ سایت محضرباشی مراجعه کن."
    )

    await update.message.reply_text(reply)
    await send_voice(update.effective_chat.id, reply)

async def callback_handler(update: Update, context: CallbackContext):
    # اگر دکمه‌ای اضافه شد بعداً می‌تونیم این رو گسترش بدیم
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("درخواست صوتی در حال آماده‌سازی است...")

# ثبت هندلرها
application.add_handler(CommandHandler("start", start_handler))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
application.add_handler(CallbackQueryHandler(callback_handler))

# --- رویدادهای FastAPI برای startup/shutdown ---
@app.on_event("startup")
async def on_startup():
    # initialize & start application (PTB)
    await application.initialize()
    await application.start()
    # ست کردن وبهوک
    await application.bot.set_webhook(WEBHOOK_URL)
    print("✅ Webhook set to:", WEBHOOK_URL)

@app.on_event("shutdown")
async def on_shutdown():
    await application.stop()
    await application.shutdown()

# --- مسیر وبهوک برای تلگرام ---
@app.post(f"/{TOKEN}")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    # پردازش آسنکرون آپدیت توسط PTB
    asyncio.create_task(application.process_update(update))
    return {"ok": True}
