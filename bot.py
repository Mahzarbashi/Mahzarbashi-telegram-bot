from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import logging
import os

# --- تنظیمات لاگ ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("mahzarbashi-bot")

# --- Flask app ---
flask_app = Flask(__name__)

# --- توکن ربات ---
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
bot = Bot(TOKEN)

# --- سوالات متداول ---
FAQ = [
    ("چگونه وقت مشاوره رزرو کنم؟", "برای رزرو وقت مشاوره از لینک زیر استفاده کنید:\nhttps://mahzarbashi.ir/رزرو-وقت-مشاوره-وکیل-پایه-یک-دادگستری/"),
    ("آیا مشاوره رایگان است؟", "برخی مشاوره‌ها رایگان و برخی با هزینه هستند؛ لطفاً صفحه رزرو را بررسی کنید."),
    ("مراحل گرفتن مهریه چیست؟", "برای دریافت مهریه می‌توانید از اجرای ثبت یا دادگاه خانواده اقدام کنید."),
    ("مدارک لازم برای طلاق چیست؟", "مدارک کامل در سایت محضرباشی قابل مشاهده است."),
]

# --- دکمه‌های منو ---
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📌 سوالات رایج", callback_data="faq")],
        [InlineKeyboardButton("📝 رزرو مشاوره", url="https://mahzarbashi.ir/رزرو-وقت-مشاوره-وکیل-پایه-یک-دادگستری/")],
        [InlineKeyboardButton("🌐 ورود به سایت", url="https://mahzarbashi.ir/")],
    ])

# --- هندلرها ---
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 😊 به ربات محضرباشی خوش آمدید.\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=main_menu_keyboard()
    )

async def faq_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton(q, callback_data=f"faq_{i}")] for i, (q, _) in enumerate(FAQ)]
    await query.edit_message_text("📌 سوالات متداول:", reply_markup=InlineKeyboardMarkup(keyboard))

async def faq_answer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    idx = int(query.data.split("_", 1)[1])
    q, a = FAQ[idx]
    await query.edit_message_text(f"❓ {q}\n\n💡 پاسخ:\n{a}")

# --- راه‌اندازی Application ---
app_builder = ApplicationBuilder().token(TOKEN).build()
app_builder.add_handler(CommandHandler("start", start_handler))
app_builder.add_handler(CallbackQueryHandler(faq_menu_handler, pattern="faq$"))
app_builder.add_handler(CallbackQueryHandler(faq_answer_handler, pattern="faq_"))

# --- Webhook route ---
@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    import asyncio
    asyncio.run(app_builder.process_update(update))
    return "OK"

# --- Route اصلی برای بررسی ---
@flask_app.route("/")
def index():
    return "ربات محضرباشی فعال است ✅"

# --- اجرای Flask ---
if __name__ == "__main__":
    # قبل از اجرا روی Render، Webhook را روی تلگرام ست کنید:
    # bot.set_webhook(url="https://<YOUR-RENDER-URL>/" + TOKEN)
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
