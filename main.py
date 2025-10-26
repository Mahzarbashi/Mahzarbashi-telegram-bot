import os
import asyncio
import tempfile
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    MessageHandler, 
    ContextTypes, 
    filters
)
from gtts import gTTS

# -----------------------------
# تنظیمات اولیه
# -----------------------------
TOKEN = os.environ.get("TELEGRAM_TOKEN", "8249435097:AAGOIS7GfwBayCTSZGFahbMhYcZDFxzSGAg")
WEBHOOK_URL = f"https://mahzarbashi-telegram-bot-1-usa9.onrender.com/{TOKEN}"

# -----------------------------
# توابع کمکی
# -----------------------------
async def send_voice(chat_id: int, text: str, context: ContextTypes.DEFAULT_TYPE):
    """تبدیل پاسخ متنی به فایل صوتی و ارسال"""
    tts = gTTS(text=text, lang='fa')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tts.save(tmp_file.name)
        await context.bot.send_audio(chat_id=chat_id, audio=open(tmp_file.name, 'rb'), title="پاسخ صوتی 🎧")

# -----------------------------
# دستور شروع
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    intro = (
        "🌸 سلام! من ربات رسمی حقوقی محضرباشی هستم.\n"
        "این ربات توسط *نسترن بنی‌طبا* ساخته شده 💫\n"
        "من می‌تونم به سؤالات حقوقی شما پاسخ بدم — مثل مهریه، طلاق، ارث، اجاره و غیره.\n"
        "سؤالت رو بپرس تا راهنماییت کنم ⚖️"
    )
    await update.message.reply_text(intro, parse_mode="Markdown")
    await send_voice(update.effective_chat.id, intro, context)

# -----------------------------
# پاسخ به سؤالات حقوقی
# -----------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    reply = ""

    if any(word in text for word in ["طلاق", "جدا", "ازدواج"]):
        reply = (
            "در موضوع طلاق، اگر زن بخواهد طلاق بگیرد باید یکی از شروط ضمن عقد یا عسر و حرج را ثابت کند. "
            "در غیر این صورت، فقط با رضایت شوهر ممکن است. "
            "در طلاق توافقی هر دو باید در دفتر خدمات قضایی حاضر شوند. "
            "برای مراحل دقیق‌تر، به بخش مشاوره سایت محضرباشی مراجعه کن 🌐"
        )

    elif any(word in text for word in ["مهریه", "سکه", "حق زن"]):
        reply = (
            "مهریه حق قانونی زن است و هر زمان بخواهد می‌تواند آن را مطالبه کند. "
            "اگر عندالاستطاعه باشد، مرد باید توان مالی خود را ثابت کند. "
            "در صورت امتناع، امکان توقیف اموال یا حتی حکم جلب وجود دارد ⚖️"
        )

    elif any(word in text for word in ["اجاره", "مستأجر", "تخلیه", "ملک"]):
        reply = (
            "در قرارداد اجاره، مستأجر موظف است ملک را طبق تاریخ مشخص تخلیه کند و موجر مبلغ رهن را بازگرداند. "
            "در اختلافات مربوط به تمدید یا تخلیه، شورای حل اختلاف صلاحیت دارد 🏠"
        )

    elif any(word in text for word in ["ارث", "وراثت", "وصیت"]):
        reply = (
            "سهم‌الارث هر شخص طبق طبقه و درجه خویشاوندی مشخص است. "
            "مثلاً فرزندان در طبقه اول ارث قرار دارند و در نبود آن‌ها والدین یا خواهر و برادر ارث می‌برند 👪"
        )

    else:
        reply = (
            "سؤال شما بررسی شد اما نیاز به جزئیات بیشتری دارد. "
            "لطفاً سؤال را واضح‌تر بنویس یا از مشاوره سایت محضرباشی استفاده کن 🌐"
        )

    await update.message.reply_text(reply)
    await send_voice(update.effective_chat.id, reply, context)

# -----------------------------
# اجرای امن برای Render (بدون RuntimeError)
# -----------------------------
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # حذف و تنظیم وبهوک جدید
    await app.bot.delete_webhook()
    await app.bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook تنظیم شد: {WEBHOOK_URL}")

    await app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", "10000")),
        url_path=TOKEN,
        webhook_url=WEBHOOK_URL,
    )

# این بخش باعث میشه Render خطای loop نده
try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
except RuntimeError:
    asyncio.run(main())
