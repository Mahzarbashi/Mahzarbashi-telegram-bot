import os
import asyncio
import logging
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)

# ---- تنظیم لاگ‌ها
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---- توکن ربات (اگر خواستی امن‌ترش کنی، از ENV بخون)
TOKEN = "8310741380:AAHRrADEytsjTVZYtJle71e5twxFxqr556c"

# ---- Flask app که Render با gunicorn آن را اجرا می‌کند
flask_app = Flask(__name__)

# ---- برنامه تلگرام
application = ApplicationBuilder().token(TOKEN).build()

# ---- سوالات متداول (۲۰ سوال نمونه)
FAQ = [
    ("چطور وقت مشاوره رزرو کنم؟",
     "روی دکمه «📝 رزرو مشاوره تخصصی» بزن یا به لینک رزرو برو:\nhttps://mahzarbashi.ir/رزرو-وقت-مشاوره-وکیل-پایه-یک-دادگستری/"),
    ("هزینه مشاوره چقدر است؟",
     "بسته به نوع پرونده و مدت‌زمان متفاوته. تعرفه به‌روز داخل صفحه رزرو نمایش داده می‌شود."),
    ("مدارک لازم برای طلاق چیست؟",
     "کارت ملی و شناسنامه، عقدنامه و مدارک مرتبط. برای بررسی دقیق حتماً با وکیل صحبت کنید."),
    ("نحوه مطالبه مهریه چگونه است؟",
     "از طریق اجرای ثبت یا دادگاه خانواده قابل پیگیری است. انتخاب مسیر وابسته به جزئیات پرونده است."),
    ("حضانت فرزند چگونه تعیین می‌شود؟",
     "اصل بر مصلحت طفل است. سن، شرایط والدین و نظر کارشناسی ملاک است."),
    ("نفقه شامل چه مواردی است؟",
     "مسکن، پوشاک، درمان و سایر نیازهای متعارف. امکان مطالبه معوقه هم وجود دارد."),
    ("شروط ضمن عقد چه اهمیتی دارد؟",
     "می‌تواند حقوقی مثل حق تحصیل/اشتغال/طلاق را تسهیل کند. قبل یا حین عقد قابل درج است."),
    ("ممنوع‌الخروجی را چگونه پیگیری کنم؟",
     "علت را باید مشخص کرد (پرونده قضایی/بدهی و ...). سپس درخواست رفع ممنوع‌الخروجی می‌دهیم."),
    ("ثبت شرکت چه مدارکی می‌خواهد؟",
     "اطلاعات شرکا، نام و موضوع، آدرس، اساسنامه و مدارک هویتی. جزئیات با نوع شرکت فرق می‌کند."),
    ("چک برگشتی را چگونه پیگیری کنم؟",
     "هم از مسیر حقوقی و هم کیفری بسته به شرایط. مشاوره تخصصی لازم است."),
    ("قرارداد مشارکت را تنظیم می‌کنید؟",
     "بله؛ تنظیم تخصصی قرارداد از خدمات اصلی ماست تا ریسک‌ها پوشش داده شود."),
    ("تخلیه ملک چقدر زمان می‌برد؟",
     "بسته به نوع قرارداد/رهن/اجاره و مدارک، زمان متفاوته. وکیل مسیر سریع‌تر را پیشنهاد می‌دهد."),
    ("سرقفلی و حق کسب چه تفاوتی دارند؟",
     "مفاهیم نزدیک اما با آثار متفاوت در قانون روابط موجر و مستأجر. بررسی موردی لازم است."),
    ("افترا و نشر اکاذیب چطور پیگیری می‌شود؟",
     "با طرح شکایت کیفری و ارائه ادله. بهتر است متن و مدارک قبل از شکایت بررسی شود."),
    ("تجربه کار با محضرباشی چطور است؟",
     "پرونده‌ها مرحله‌به‌مرحله در کنار شما پیش می‌رود و پیگیری شفاف داریم."),
    ("آیا امکان پیگیری آنلاین پرونده هست؟",
     "بله، پس از عقد قرارداد، وضعیت پرونده به‌صورت منظم اطلاع‌رسانی می‌شود."),
    ("ساعت‌های پاسخگویی چطور است؟",
     "رزرو آنلاین ۲۴ساعته باز است؛ تماس تلفنی در ساعات اداری."),
    ("آیا قرارداد الکترونیکی معتبر است؟",
     "بله؛ با امضای الکترونیکی معتبر. اما در برخی موارد نسخه حضوری پیشنهاد می‌شود."),
    ("برای انتقال ملک چه نکاتی را رعایت کنم؟",
     "استعلام ثبتی، بررسی بدهی‌ها، تنظیم مبایعه‌نامه دقیق و پرداخت امن."),
    ("از کجا شروع کنم؟",
     "از منوی زیر یکی را انتخاب کن: سوالات رایج، رزرو مشاوره تخصصی یا ورود به سایت."),
]

# ---- هندلرهای ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📌 سوالات رایج", callback_data="faq")],
        [InlineKeyboardButton("📝 رزرو مشاوره تخصصی",
                              url="https://mahzarbashi.ir/رزرو-وقت-مشاوره-وکیل-پایه-یک-دادگستری/")],
        [InlineKeyboardButton("🌐 ورود به سایت محضرباشی", url="https://mahzarbashi.ir/")],
    ]
    await update.message.reply_text(
        "سلام 🙂 به ربات محضرباشی خوش اومدی!\nلطفاً یک گزینه را انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def show_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton(q, callback_data=f"ans_{i}")]
                for i, (q, _) in enumerate(FAQ)]
    await query.edit_message_text(
        "لطفاً یکی از سوالات زیر را انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    idx = int(query.data.split("_")[1])
    q, a = FAQ[idx]
    await query.answer()
    await query.edit_message_text(f"❓ {q}\n\n💡 پاسخ:\n{a}")

# ---- ثبت هندلرها
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(show_faq, pattern="^faq$"))
application.add_handler(CallbackQueryHandler(show_answer, pattern="^ans_"))

# ---- آماده‌سازی اپ تلگرام هنگام بالا آمدن سرور
async def _startup():
    await application.initialize()
    # اگر Render آدرس بیرونی را در ENV گذاشته باشد، وبهوک را ست می‌کنیم
    ext = os.getenv("RENDER_EXTERNAL_URL")
    if ext:
        try:
            await application.bot.set_webhook(url=f"{ext}/{TOKEN}")
            logger.info("Webhook set to %s/%s", ext, TOKEN)
        except Exception as e:
            logger.exception("Failed to set webhook: %s", e)
    await application.start()

# در زمان import ماژول (gunicorn)، برنامه تلگرام را استارت کن
asyncio.get_event_loop().run_until_complete(_startup())

# ---- مسیر سلامت برای Render
@flask_app.get("/health")
def health():
    return jsonify(status="ok"), 200

# ---- مسیر دریافت آپدیت‌های تلگرام (همان مسیری که وبهوک رویش ست شده)
@flask_app.post(f"/{TOKEN}")
def telegram_webhook():
    data = request.get_json(silent=True, force=True) or {}
    try:
        update = Update.de_json(data, application.bot)
        asyncio.get_event_loop().create_task(application.process_update(update))
    except Exception as e:
        logger.exception("Update processing failed: %s", e)
    return "OK", 200
