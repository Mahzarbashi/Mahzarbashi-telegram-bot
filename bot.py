import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    CallbackQueryHandler,
    filters
)

# گرفتن توکن از متغیر محیطی
TOKEN = os.getenv("BOT_TOKEN", "8310741380:AAHRrADEytsjTVZYtJle71e5twxFxqr556c")

# ساخت اپلیکیشن Flask برای Render
app = Flask(__name__)
flask_app = app  # خیلی مهمه برای gunicorn

# تعریف سوالات رایج
faq_list = [
    ("چگونه وقت مشاوره رزرو کنم؟", "برای رزرو وقت مشاوره روی دکمه رزرو مشاوره بزنید."),
    ("آیا مشاوره رایگان است؟", "بسته به نوع مشاوره هزینه متفاوت است. لطفاً به سایت مراجعه کنید."),
    ("مراحل گرفتن مهریه چیست؟", "مهریه طبق قانون قابل مطالبه است. برای مشاوره تخصصی به وکلای ما مراجعه کنید."),
    ("مدارک لازم برای طلاق چیست؟", "مدارک موردنیاز در سایت محضرباشی موجود است."),
]

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📌 سوالات رایج", callback_data="faq")],
        [InlineKeyboardButton("📝 رزرو مشاوره", url="https://mahzarbashi.ir/رزرو-وقت-مشاوره-وکیل-پایه-یک-دادگستری/")],
        [InlineKeyboardButton("🌐 ورود به سایت", url="https://mahzarbashi.ir/")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "سلام 🙂\nبه ربات محضرباشی خوش آمدید!\nلطفاً یکی از گزینه‌ها را انتخاب کنید:",
        reply_markup=reply_markup
    )

# نمایش سوالات رایج
async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton(q, callback_data=f"answer_{i}")] for i, (q, _) in enumerate(faq_list)]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("لطفاً یکی از سوالات زیر را انتخاب کنید:", reply_markup=reply_markup)

# نمایش پاسخ سوال
async def show_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    index = int(query.data.split("_")[1])
    await query.answer()
    await query.edit_message_text(
        f"❓ {faq_list[index][0]}\n\n💡 پاسخ:\n{faq_list[index][1]}"
    )

# ساخت اپلیکیشن تلگرام
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(faq, pattern="faq"))
application.add_handler(CallbackQueryHandler(show_answer, pattern="answer_"))

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put(update)
    return "ok"

@app.route('/')
def index():
    return "Mahzarbashi Bot is running successfully ✅"

if __name__ == '__main__':
    application.run_polling()
