import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from gtts import gTTS
import tempfile

# گرفتن توکن از محیط Render
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN تعریف نشده! لطفاً Environment Variables را در Render تنظیم کن.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام 👋 خوش اومدی به ربات محضرباشی!\nسؤالت رو بنویس تا راهنمایی‌ت کنم.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    response_text = f"این یک راهنمایی اولیه است درباره: {text}\nبرای مشاوره تخصصی وارد سایت شو 🌐 mahzarbashi.ir"

    # پاسخ متنی
    await update.message.reply_text(response_text)

    # پاسخ صوتی
    tts = gTTS(text=response_text, lang='fa')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tts.save(tmp.name)
        await update.message.reply_audio(audio=open(tmp.name, 'rb'))
        os.remove(tmp.name)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 ربات محضرباشی در حال اجراست...")
    app.run_polling()

if __name__ == "__main__":
    main()
