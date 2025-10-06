import os
from telegram.ext import Application, CommandHandler

TOKEN = "8249435097:AAF8PSgEXDVYWYBIXn_q45bHKID_aYDAtqw"

async def start(update, context):
    await update.message.reply_text("سلام 👋 من ربات محضرباشی هستم.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        url_path=TOKEN,
        webhook_url=f"https://mahzarbashi-bot.onrender.com/{TOKEN}"
    )

if __name__ == "__main__":
    main()
