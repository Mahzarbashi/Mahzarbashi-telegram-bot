import os
import logging
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# تنظیمات لاگ
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# گرفتن توکن ربات از متغیر محیطی
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("⚠️ لطفاً متغیر محیطی BOT_TOKEN را در Render ست کنید.")

# ساخت اپلیکیشن تلگرام
app_telegram = ApplicationBuilder().token(TOKEN).build()

# Flask برای مدیریت Webhook
flask_app = Flask(__name__)

# --- سوالات متداول ---
faq_list = [
    ("چگونه وقت مشاوره رزرو کنم؟", "برای رزرو وقت مشاوره از لینک زیر استفاده کنید:\nhttps://mahzarbashi.ir/رزرو-وقت-مشاوره-وکیل-پایه-یک-دادگستری/"),
    ("آیا مشاوره رایگان است؟", "بسته به نوع خدمت ممکن است رایگان یا غیررایگان باشد."),
    ("مراحل گرفتن مهریه چیست؟", "جهت دریافت مهریه، از طریق دادگاه خانواده اقدام کنید."),
    ("مدارک لازم برای طلاق چیست؟", "مدارک کامل در سایت محضرباشی موجود است."),
]

# --- ساخت منوی اصلی ---
def main_menu():
    keyboard = [
        [InlineKeyboardButton("📌 سوالات رایج", callback_data="faq")],
        [InlineKeyboardButton("📝 رزرو مشاوره", url="https://mahzarbashi.ir/رزرو-وقت-مشاوره-وکیل-پایه-یک-دادگستری/")],
        [InlineKeyboardButton("🌐 ورود به سایت", url="https://mahzarbashi.ir/")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- دستور /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 😊\nبه ربات محضرباشی خوش آمدید.\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=main_menu()
    )

# --- نمایش سوالات متداول ---
async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton(q, callback_data=f"answer_{i}")] for i, (q, _) in enumerate(faq_list)]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("لطفاً یکی از سوالات زیر را انتخاب کنید:", reply_markup=reply_markup)

# --- نمایش پاسخ سوال انتخابی ---
async def show_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    index = int(query.data.split("_")[1])
    await query.answer()
    await query.edit_message_text(f"❓ {faq_list[index][0]}\n\n💡 پاسخ:\n{faq_list[index][1]}")

# اضافه کردن هندلرها
app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(CallbackQueryHandler(faq, pattern="faq"))
app_telegram.add_handler(CallbackQueryHandler(show_answer, pattern="answer_"))

# --- مسیر Webhook برای Telegram ---
@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), app_telegram.bot)
    app_telegram.update_queue.put(update)
    return "OK", 200

# صفحه اصلی تست سرور
@flask_app.route("/")
def home():
