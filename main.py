import os
import asyncio
import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from gtts import gTTS

# جلوگیری از ارور event loop تکراری در Render
nest_asyncio.apply()

# دریافت توکن از محیط Render
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("❌ توکن تلگرام پیدا نشد! لطفاً TELEGRAM_TOKEN را در Render تنظیم کنید.")

# 🔹 پیام خوش‌آمد اولیه
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 سلام! این ربات توسط *نسترن بنی‌طبا* ساخته شده است.\n\n"
        "من پاسخگوی سؤالات حقوقی شما هستم ⚖️.\n"
        "سؤال حقوقی‌ات رو بنویس تا هم به‌صورت متنی و هم صوتی راهنمایی‌ات کنم 💬🎧"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

# 🔹 پاسخ به پیام‌های متنی
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # بررسی اینکه پیام حقوقی است یا نه
    keywords = ["طلاق", "مهریه", "قرارداد", "دادگاه", "شکایت", "حق", "وکیل", "اجاره", "ملک", "وصیت", "دیوان", "محکومیت"]
    if any(word in text for word in keywords):
        reply_text = (
            f"📘 پاسخ حقوقی:\n"
            f"در مورد «{text}»، طبق قوانین حقوقی ایران، این موضوع دارای ابعاد مختلفی است. "
            f"به طور کلی، حقوق و تکالیف هر طرف باید طبق قرارداد یا قانون مشخص شود.\n\n"
            f"اگر جزئیات بیشتری داری، بهتره در سایت محضرباشی در بخش «مشاوره حقوقی» ثبت کنی:\n"
            f"https://mahzarbashi.ir"
        )
        await update.message.reply_text(reply_text)

        # تولید و ارسال پاسخ صوتی
        tts = gTTS(text=reply_text, lang='fa')
        tts.save("reply.mp3")
        with open("reply.mp3", "rb") as voice_file:
            await update.message.reply_voice(voice=voice_file)

    else:
        await update.message.reply_text(
            "⚖️ لطفاً فقط سؤال حقوقی بپرس تا بتونم دقیق راهنمایی‌ات کنم.\n"
            "برای سؤالات عمومی‌تر به سایت محضرباشی برو:\nhttps://mahzarbashi.ir"
        )

# 🔹 اجرای اصلی برنامه
async def main():
    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )

    # افزودن هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # تنظیم Webhook برای Render
    port = int(os.environ.get("PORT", 8080))
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    if not render_url:
        raise ValueError("❌ مقدار RENDER_EXTERNAL_URL تنظیم نشده است!")

    webhook_url = f"{render_url}/{TOKEN}"
    print(f"✅ Webhook set to: {webhook_url}")

    await application.initialize()
    await application.start()
    await application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TOKEN,
        webhook_url=webhook_url,
    )

# 🧠 اجرای بدون ارور در Render
if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except RuntimeError:
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        new_loop.run_until_complete(main())
