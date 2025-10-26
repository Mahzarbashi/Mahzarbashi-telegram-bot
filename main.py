import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from gtts import gTTS
import nest_asyncio

nest_asyncio.apply()

TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("❌ توکن تلگرام پیدا نشد! لطفاً TELEGRAM_TOKEN را در Render تنظیم کنید.")

# 🟢 پیام خوش‌آمد
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 سلام! این ربات توسط *نسترن بنی‌طبا* ساخته شده است.\n\n"
        "من پاسخگوی سؤالات حقوقی شما هستم. می‌توانید سؤال خود را در مورد مسائل حقوقی بنویسید "
        "و من هم به‌صورت متنی و هم صوتی پاسخ می‌دهم.\n\n"
        "⚖️ لطفاً سؤال حقوقی خود را بپرسید..."
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

# 🟢 تابع تولید پاسخ صوتی و متنی
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()

    # فقط پاسخ به سوالات حقوقی
    if any(word in user_text for word in ["طلاق", "مهریه", "وصیت", "اجاره", "قرارداد", "محکمه", "دادگاه", "شکایت", "حق", "وکیل", "وراثت"]):
        response_text = (
            f"پاسخ حقوقی شما:\n\n"
            f"در مورد «{user_text}»، طبق قوانین حقوقی ایران، این موضوع نیاز به بررسی دقیق دارد. "
            f"به‌طور کلی، حق و تکلیف طرفین باید بر اساس قرارداد یا قانون مشخص شود.\n\n"
            f"در صورتی که جزئیات بیشتری دارید، می‌توانید در سایت محضرباشی بخش «مشاوره حقوقی» ثبت کنید:\n"
            f"https://mahzarbashi.ir"
        )
        await update.message.reply_text(response_text)

        # تولید پاسخ صوتی
        tts = gTTS(text=response_text, lang="fa")
        tts.save("response.mp3")
        with open("response.mp3", "rb") as audio:
            await update.message.reply_voice(voice=audio)

    else:
        await update.message.reply_text(
            "⚖️ لطفاً فقط سؤال حقوقی بپرسید تا بتوانم پاسخ دقیق بدهم.\n"
            "برای سؤالات دیگر، لطفاً به وب‌سایت محضرباشی مراجعه کنید:\nhttps://mahzarbashi.ir"
        )

# 🟢 ساخت اپلیکیشن
async def main():
    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # تنظیم Webhook برای Render
    port = int(os.environ.get("PORT", 8080))
    render_url = os.environ.get("RENDER_EXTERNAL_URL")

    if not render_url:
        raise ValueError("❌ متغیر RENDER_EXTERNAL_URL تنظیم نشده است!")

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

if __name__ == "__main__":
    asyncio.run(main())
