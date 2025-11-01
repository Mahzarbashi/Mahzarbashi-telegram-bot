import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from flask import Flask, request

TOKEN = os.environ.get("BOT_TOKEN")
app = Flask(__name__)

application = Application.builder().token(TOKEN).build()

# نمونه هندلر
async def start(update, context):
    await update.message.reply_text("سلام! من ربات محضرباشی‌ام 🤖")

application.add_handler(CommandHandler("start", start))

@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    update = await request.get_json()
    if update:
        await application.process_update(
            telegram.Update.de_json(update, application.bot)
        )
    return "OK"

@app.route("/", methods=["GET"])
def index():
    return "Bot is running ✅"

if __name__ == "__main__":
    import asyncio
    async def main():
        await application.initialize()
        await application.start()
        await application.updater.start_webhook(
            listen="0.0.0.0",
            port=int(os.environ.get("PORT", 10000)),
            url_path=TOKEN,
            webhook_url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
        )
        print("Webhook set and bot started ✅")
        await asyncio.Event().wait()  # keeps bot running

    asyncio.run(main())
