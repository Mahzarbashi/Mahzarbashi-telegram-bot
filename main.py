import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8249435097:AAEqSwTL8Ah8Kfyzo9Z_iQE97OVUViXtOmY"

# پاسخ ساده برای تست
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ربات محضرباشی با موفقیت فعاله ✅")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)

# ساخت برنامه
app = ApplicationBuilder().token(TOKEN).build()

# هندلرها
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# اجرای webhook
PORT = int(os.environ.get("PORT", 8443))
URL = "https://mahzarbashi-bot.onrender.com"  # 👈 آدرس دقیق پروژه روی Render

if __name__ == "__main__":
    import asyncio

    async def main():
        await app.initialize()
        # تنظیم وبهوک
        await app.bot.set_webhook(f"{URL}/webhook")
        # اجرای وبسرور داخلی
        await app.start()
        print(f"🚀 Webhook set at {URL}/webhook and bot is running...")
        await app.updater.start_webhook(listen="0.0.0.0", port=PORT, url_path="/webhook", webhook_url=f"{URL}/webhook")
        await app.updater.idle()

    asyncio.run(main())
