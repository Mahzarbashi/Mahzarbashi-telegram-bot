import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# فعال کردن لاگ‌ها برای خطایابی
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# توکن ربات
TOKEN = "8310741380:AAHRrADEytsjTVZYtJle71e5twxFxqr556c"

# سوالات متداول
faq_list = [
    ("چگونه وقت مشاوره رزرو کنم؟", "برای رزرو وقت مشاوره روی دکمه 'رزرو مشاوره' بزنید."),
    ("آیا مشاوره رایگان است؟", "بسته به نوع مشاوره هزینه متفاوت است. لطفاً به سایت مراجعه کنید."),
    ("مدارک لازم برای طلاق چیست؟", "برای اطلاعات کامل به بخش مقالات سایت محضرباشی مراجعه کنید."),
    ("مراحل گرفتن مهریه چیست؟", "مهریه طبق قانون قابل مطالبه است. برای مشاوره تخصصی به وکلای ما مراجعه کنید."),
    ("آیا حضانت فرزند قابل انتقال است؟", "بله، اما نیازمند بررسی قضایی است."),
    ("برای ثبت شرکت چه مدارکی نیاز است؟", "مدارک شناسایی، اساسنامه و آدرس محل شرکت لازم است."),
    ("آیا امکان پیگیری پرونده در سایت وجود دارد؟", "بله، از طریق بخش 'پیگیری پرونده' در سایت محضرباشی."),
    ("چگونه وکیل انتخاب کنم؟", "وکلای محضرباشی پروفایل کامل دارند، از آنجا انتخاب کنید."),
    ("آیا تنظیم قرارداد انجام می‌دهید؟", "بله، وکلای ما قراردادها را تنظیم می‌کنند."),
    ("چگونه شکایت کیفری ثبت کنم؟", "به بخش کیفری سایت بروید یا از وکلای ما مشاوره بگیرید."),
]

# منوی اصلی
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📌 سوالات رایج", callback_data="faq")],
        [InlineKeyboardButton("📝 درخواست مشاوره حقوقی", url="https://mahzarbashi.ir/رزرو-وقت-مشاوره-وکیل-پایه-یک-دادگستری/")],
        [InlineKeyboardButton("🌐 ورود به سایت محضرباشی", url="https://mahzarbashi.ir/")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "سلام 🙂\nبه ربات محضرباشی خوش اومدید!\nلطفاً یکی از گزینه‌ها رو انتخاب کنید:",
        reply_markup=reply_markup
    )

# نمایش سوالات متداول
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

# اجرای ربات
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(faq, pattern="faq"))
    app.add_handler(CallbackQueryHandler(show_answer, pattern="answer_"))

    app.run_polling()

if __name__ == "__main__":
    main()
