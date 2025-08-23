import logging
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ----------------- تنظیمات اولیه -----------------
TOKEN = "8310741380:AAHRrADEytsjTVZYtJle71e5twxFxqr556c"
WEBHOOK_URL = "https://mahzarbashi-telegram-bot.onrender.com"

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------- سوالات و پاسخ‌های متداول -----------------
faq = {
    "مهریه": "مهریه حق قانونی زن است و هر زمان می‌تواند آن را مطالبه کند.",
    "طلاق توافقی": "طلاق توافقی با رضایت طرفین انجام می‌شود و زمان کمتری می‌برد.",
    "حضانت فرزند": "حضانت تا ۷ سالگی با مادر و بعد از آن با پدر است مگر دادگاه خلافش را تشخیص دهد.",
    "نفقه": "نفقه شامل مسکن، پوشاک و سایر نیازهای زن است و مرد موظف به پرداخت آن است.",
    "چک برگشتی": "با ثبت چک در سامانه صیاد، پیگیری چک برگشتی سریع‌تر و راحت‌تر می‌شود.",
    "دیه": "میزان دیه هر سال توسط قوه قضاییه اعلام می‌شود و می‌تواند نقد یا اقساط پرداخت شود.",
    "جرائم اینترنتی": "در صورت هک یا کلاهبرداری اینترنتی، سریعاً به پلیس فتا گزارش دهید.",
    "سفته و برات": "برای وصول سفته و برات، حتماً باید در مهلت قانونی اقدام شود.",
    "توقیف اموال": "برای توقیف اموال بدهکار، ابتدا باید حکم قطعی از دادگاه گرفته شود.",
    "افترا و توهین": "انتشار مطالب خلاف واقع یا توهین‌آمیز در فضای مجازی جرم محسوب می‌شود.",
    "کلاهبرداری": "در صورت مواجهه با کلاهبرداری، سریعاً شکایت کیفری ثبت کنید.",
    "اخراج از کار": "در صورت اخراج غیرقانونی، می‌توانید به اداره کار شکایت کنید.",
    "بیمه بیکاری": "کارگرانی که به دلیل غیرارادی بیکار می‌شوند، می‌توانند بیمه بیکاری دریافت کنند.",
    "سهم‌الارث": "سهم‌الارث بین وراث بر اساس قانون مدنی تقسیم می‌شود.",
    "وصیت‌نامه": "وصیت‌نامه رسمی در دفاتر اسناد رسمی ثبت می‌شود و اعتبار بیشتری دارد.",
    "ملک مشاع": "برای فروش ملک مشاع، رضایت همه مالکین لازم است مگر دادگاه دستور دهد.",
    "جرائم رانندگی": "در صورت اعتراض به جریمه رانندگی، باید در سامانه راهور درخواست ثبت کنید.",
    "مهاجرت": "برای مشاوره مهاجرتی بهتر است با وکیل متخصص مشورت کنید.",
    "قرارداد اجاره": "قرارداد اجاره باید در سامانه املاک ثبت شود تا اعتبار قانونی داشته باشد.",
    "مشاوره تخصصی": "برای مشاوره تخصصی وارد لینک زیر شوید:\nhttps://mahzarbashi.ir/رزرو-وقت-مشاوره-وکیل-پایه-یک-دادگستری/"
}

# ----------------- استارت ربات -----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📌 سوالات رایج", callback_data="faq")],
        [InlineKeyboardButton("📝 رزرو مشاوره تخصصی", url="https://mahzarbashi.ir/رزرو-وقت-مشاوره-وکیل-پایه-یک-دادگستری/")],
        [InlineKeyboardButton("🌐 ورود به سایت", url="https://mahzarbashi.ir")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام 👋\nبه ربات محضرباشی خوش آمدید 🌿\nلطفاً یکی از گزینه‌ها را انتخاب کنید:", reply_markup=reply_markup)

# ----------------- لیست سوالات رایج -----------------
async def show_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton(q, callback_data=f"answer_{q}")] for q in faq.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("📌 سوالات متداول:", reply_markup=reply_markup)

# ----------------- پاسخ به سوالات -----------------
async def show_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    question = query.data.split("_", 1)[1]
    answer = faq.get(question, "پاسخی یافت نشد.")
    await query.edit_message_text(f"❓ سوال: {question}\n\n💡 پاسخ: {answer}")

# ----------------- پاسخ به پیام‌های متنی -----------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    answer = faq.get(text, "برای مشاوره تخصصی به لینک زیر بروید:\nhttps://mahzarbashi.ir/رزرو-وقت-مشاوره-وکیل-پایه-یک-دادگستری/")
    await update.message.reply_text(answer)

# ----------------- ساخت اپلیکیشن Flask -----------------
flask_app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(show_faq, pattern="^faq$"))
application.add_handler(CallbackQueryHandler(show_answer, pattern="^answer_"))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK", 200

if __name__ == "__main__":
    application.run_webhook(
        listen="0.0.0.0",
        port=10000,
        url_path=TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
    )
