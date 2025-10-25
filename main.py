import os
import tempfile
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from gtts import gTTS

# -----------------------------
# توکن تلگرام
# -----------------------------
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    print("⚠️ متغیر محیطی TELEGRAM_TOKEN پیدا نشد! از توکن موقت استفاده می‌شود.")
    TOKEN = "8249435097:AAGOIS7GfwBayCTSZGFahbMhYcZDFxzSGAg"

bot = Bot(token=TOKEN)

# -----------------------------
# پیام خوش‌آمد و معرفی
# -----------------------------
INTRO_TEXT = (
    "👋 سلام! من دستیار حقوقی محضرباشی هستم.\n"
    "این ربات توسط نسترن بنی‌طبا ساخته شده است ⚖️\n"
    "من می‌تونم به سؤالات حقوقی شما پاسخ بدم — هم متنی و هم صوتی 🎧\n"
    "کافیه سؤال حقوقی‌ات رو بفرستی تا راهنماییت کنم."
)

# -----------------------------
# پاسخ‌های حقوقی
# -----------------------------
def legal_answer(text):
    text = text.strip().lower()

    if any(word in text for word in ["ازدواج", "نکاح"]):
        return (
            "💍 ازدواج یکی از عقود مهم در قانون مدنی ایران است. "
            "برای صحت ازدواج، باید رضایت کامل زن و مرد وجود داشته باشد و "
            "عقد توسط دو شاهد مرد اجرا شود. "
            "اگر یکی از طرفین اهلیت قانونی نداشته باشد، عقد باطل است. "
            "در نکاح دائم، ثبت ازدواج الزامی است و مهریه نیز جزو حقوق زن محسوب می‌شود. "
            "در موارد خاص مثل ازدواج مجدد یا ازدواج با اتباع خارجی، نیاز به اجازه رسمی وجود دارد."
        )

    elif "مهریه" in text:
        return (
            "💰 مهریه مالی است که هنگام عقد نکاح، به‌عنوان حق زن تعیین می‌شود. "
            "زن به محض جاری شدن عقد مالک مهریه است و می‌تواند هر زمان بخواهد آن را مطالبه کند. "
            "در صورت امتناع شوهر، زن می‌تواند از طریق دادگاه درخواست صدور اجراییه کند. "
            "اگر مهریه عندالمطالبه باشد، باید بلافاصله پرداخت شود. "
            "در مهریه عندالاستطاعه، زن باید توانایی مالی شوهر را اثبات کند. "
            "توصیه می‌شود همیشه مهریه به‌صورت عددی و روشن در عقدنامه ذکر شود."
        )

    elif "طلاق" in text:
        return (
            "💔 طلاق در قانون ایران به دو نوع توافقی و غیرتوافقی تقسیم می‌شود. "
            "در طلاق توافقی، زن و شوهر با رضایت متقابل جدا می‌شوند و مراحل دادگاه کوتاه‌تر است. "
            "در طلاق غیرتوافقی، یکی از طرفین باید دلایل موجه ارائه دهد، مثل عسر و حرج یا عدم پرداخت نفقه. "
            "در هر نوع طلاق، ثبت رسمی و صدور گواهی عدم امکان سازش الزامی است. "
            "پس از طلاق، حقوق مالی زن مانند مهریه و نفقه باید تسویه شود."
        )

    elif "نفقه" in text:
        return (
            "👛 نفقه یعنی تأمین نیازهای مالی و معیشتی زن توسط شوهر. "
            "شامل خوراک، پوشاک، مسکن و هزینه‌های درمانی است. "
            "اگر شوهر از پرداخت نفقه خودداری کند، زن می‌تواند از دادگاه شکایت کند. "
            "عدم پرداخت نفقه جرم محسوب می‌شود و مجازات حبس دارد. "
            "در عقد دائم، نفقه همیشه بر عهده شوهر است؛ ولی در عقد موقت فقط در صورت شرط، الزام دارد."
        )

    elif "قرارداد" in text or "عقد" in text:
        return (
            "📜 هر قراردادی برای اعتبار باید سه شرط اصلی داشته باشد: "
            "قصد و رضای طرفین، اهلیت قانونی، و موضوع مشروع. "
            "در صورت فقدان هر یک از این موارد، قرارداد باطل است. "
            "بهتر است تمام شروط و جزئیات قرارداد به‌صورت کتبی ذکر شود تا اختلافی ایجاد نشود. "
            "در قراردادهای مهم مثل اجاره، خرید و فروش، یا شراکت، تنظیم رسمی در دفترخانه توصیه می‌شود."
        )

    elif "ارث" in text or "میراث" in text:
        return (
            "⚰️ ارث به اموالی گفته می‌شود که پس از فوت شخص به وراث منتقل می‌شود. "
            "قانون، وراث را به طبقات مختلف تقسیم کرده است؛ پدر، مادر، فرزند، همسر و... "
            "سهم هر وارث طبق قانون مشخص است و زن در صورت داشتن فرزند، یک‌هشتم از اموال منقول را ارث می‌برد. "
            "برای جلوگیری از اختلاف، بهتر است تقسیم ارث با گواهی انحصار وراثت انجام شود."
        )

    elif "شکایت" in text or "دادگاه" in text or "کیفری" in text:
        return (
            "⚖️ برای ثبت شکایت، ابتدا باید نوع جرم یا دعوا مشخص شود. "
            "در شکایت کیفری مثل سرقت یا تهدید، باید در دادسرا طرح شود. "
            "در دعاوی حقوقی مثل مطالبه مهریه یا اجاره‌نامه، باید دادخواست در دفاتر خدمات قضایی ثبت گردد. "
            "همراه داشتن مدارک، کارت ملی، و مستندات الزامی است. "
            "رسیدگی ممکن است چند مرحله (بدوی، تجدیدنظر، دیوان عالی) داشته باشد."
        )

    else:
        return (
            "📚 این موضوع تخصصی‌تر است و نیاز به بررسی دقیق دارد. "
            "پیشنهاد می‌کنم برای دریافت پاسخ کامل‌تر، وارد سایت محضرباشی شوید:\n"
            "🌐 www.mahzarbashi.ir"
        )

# -----------------------------
# مدیریت پیام‌های متنی
# -----------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    answer_text = legal_answer(user_text)

    reply_text = f"{answer_text}\n\n🔊 برای شنیدن پاسخ، دکمه زیر را بزنید."
    keyboard = [[InlineKeyboardButton("🎧 گوش دادن صوتی", callback_data=f"voice:{answer_text}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(reply_text, reply_markup=reply_markup)

# -----------------------------
# تولید پاسخ صوتی با gTTS
# -----------------------------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("voice:"):
        text = query.data.replace("voice:", "")
        tts = gTTS(text=text, lang='fa')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tts.save(tmp.name)
            await bot.send_audio(chat_id=query.message.chat_id, audio=open(tmp.name, 'rb'))
        await query.edit_message_text("✅ پاسخ صوتی ارسال شد 🎧")

# -----------------------------
# راه‌اندازی ربات
# -----------------------------
application = Application.builder().token(TOKEN).build()
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
application.add_handler(CallbackQueryHandler(button_handler))

# -----------------------------
# اجرای Webhook روی Render
# -----------------------------
if __name__ == "__main__":
    hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    if not hostname:
        raise ValueError("❌ متغیر محیطی RENDER_EXTERNAL_HOSTNAME پیدا نشد!")
    url = f"https://{hostname}/{TOKEN}"
    print(f"✅ Webhook set to: {url}")

    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        url_path=TOKEN,
        webhook_url=url
    )
