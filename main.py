import os
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# گرفتن متغیرها از محیط
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# بررسی وجود کلیدها
if not TELEGRAM_TOKEN or not GROQ_API_KEY:
    raise ValueError("❌ لطفاً TELEGRAM_TOKEN و GROQ_API_KEY را در Environment Variables ست کنید.")

# ساخت Bot
bot = Bot(token=TELEGRAM_TOKEN)
updater = Updater(token=TELEGRAM_TOKEN)

# یک پاسخ ساده برای تست
def start(update: Update, context: CallbackContext):
    update.message.reply_text("سلام! ربات آماده است ✅")

def echo(update: Update, context: CallbackContext):
    update.message.reply_text(f"پیام شما: {update.message.text}\nکلید فعال است: {GROQ_API_KEY[:5]}...")

updater.dispatcher.add_handler(CommandHandler("start", start))
updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

# استارت ربات
updater.start_polling()
updater.idle()
