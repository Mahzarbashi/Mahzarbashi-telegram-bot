import os
import tempfile
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from gtts import gTTS

# ----------------------------------------
# 🎯 تنظیم توکن تلگرام
# ----------------------------------------
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    print("⚠️ متغیر محیطی TELEGRAM_TOKEN پیدا نشد! از توکن موقت استفاده می‌شود.")
    TOKEN = "8249435097:AAGOIS7GfwBayCTSZGFahbMhYcZDFxzSGAg"

bot = Bot(token=TOKEN)

# ----------------------------------------
# ⚙️ حذف وبهوک قبلی قبل از ست کردن جدید
# ----------------------------------------
import asyncio
async def reset_webhook():
    try:
        await bot.delete_webhook()
        print("🧹 Webhook قبلی با موفقیت پاک شد.")
    except Exception as e:
        print(f"⚠️ خطا در حذف وبهوک قبلی: {e}")

asyncio.run(reset_webhook())

# ----------------------------------------
# پیام خوش‌آمد و معرفی رسمی
# ----------------------------------------
INTRO_TEXT = (
    "👋 سلام! من دستیار حقوقی محضرباشی هستم.\n"
    "این ربات توسط نسترن بنی‌طبا ساخته شده است ⚖️\n"
    "من پاسخگوی سؤالات حقوقی شما هستم — هم متنی و هم صوتی 🎧\n"
    "کافیه سؤال حقوقی‌ات رو بفرستی تا راهنماییت کنم."
)

# ----------------------------------------
# تابع تولید پاسخ‌های حقوقی
# ----------------------------------------
def legal_answer(text):
    text = text.strip().lower()

    if any(word in text for word in ["ازدواج", "نکاح"]):
        return (
            "💍 ازدواج یکی از عقود مهم در قانون مدنی ایران است. "
            "برای صحت ازدواج، رضایت کامل زن و مرد، اهلیت و شاهدان لازم است. "
            "در نکاح دائم ثبت عقد الزامی است و مهریه از حقوق زن محسوب می‌شود. "
            "در موارد خاص مانند ازدواج با اتباع خارجی، نیاز به اجازه رسمی وجود دارد."
        )
    elif "مهریه" in text:
        return (
            "💰 مهریه مالی است که در زمان عقد به‌عنوان حق زن تعیین می‌شود. "
            "زن مالک آن است و هر زمان می‌تواند آن را مطالبه کند. "
            "در صورت امتناع شوهر، زن می‌تواند از دادگاه درخواست صدور اجراییه کند. "
            "در مهریه عندالاستطاعه، باید توان مالی شوهر ثابت شود."
        )
    elif "طلاق" in text:
        return (
            "💔 طلاق به دو نوع توافقی و غیرتوافقی تقسیم می‌شود. "
            "در طلاق توافقی، زوجین با رضایت جدا می‌شوند. "
            "در غیرتوافقی، یکی از طرفین باید دلایل موجه ارائه دهد مثل عسر و حرج. "
            "ثبت رسمی طلاق و تسویه حقوق مالی زن الزامی است."
        )
    elif "نفقه" in text:
        return (
            "👛 نفقه یعنی تأمین نیازهای زن مانند خوراک، پوشاک و مسکن توسط شوهر. "
            "عدم پرداخت نفقه جرم است و زن می‌تواند شکایت کند. "
            "در عقد دائم نفقه همیشه بر عهده شوهر است."
        )
    elif "قرارداد" in text or "عقد" in text:
        return (
            "📜 هر قرارداد معتبر باید سه شرط داشته باشد: قصد و رضا، اهلیت و موضوع مشروع. "
            "در غیر این صورت باطل است. "
            "توصیه می‌شود قراردادهای مهم در دفترخانه رسمی تنظیم شود."
        )
    elif "ارث" in text or "میراث" in text:
        return (
            "⚰️ ارث اموالی است که پس از فوت شخص بین وراث تقسیم می‌شود. "
            "سهم هر وارث طبق قانون مشخص است. "
            "برای تقسیم ارث، گواهی انحصار وراثت ضروری است."
        )
    elif "شکایت" in text or "دادگاه" in text or "کیفری" in text:
        return (
            "⚖️ برای شکایت باید نوع دعوا مشخص شود. "
            "شکایت کیفری در دادسرا و دعاوی حقوقی در دفاتر خدمات قضایی ثبت می‌شود. "
            "داشتن مدارک و کارت ملی ضروری است. "
            "رسیدگی ممکن است چند مرحله داشته باشد."
        )
    else:
        return (
            "📚 این موضوع تخصصی‌تر است و نیاز به بررسی دقیق دارد. "
            "پیشنهاد می‌کنم برای پاسخ کامل‌تر به سایت محضرباشی مراجعه کنید:\n"
            "🌐 www.mahzarbashi.ir"
        )

# ----------------------------------------
# پاسخ به پیام‌ها
# ----------------------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    answer_text = legal_answer(user_text)
    reply_text = f"{answer_text}\n\n🔊 برای شنیدن پاسخ، روی دکمه زیر بزنید:"
    keyboard = [[InlineKeyboardButton("🎧 گوش دادن صوتی", callback_data=f"voice:{answer_text}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(reply_text, reply_markup=reply_markup)

# ----------------------------------------
# پاسخ صوتی
# ----------------------------------------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("voice:"):
        text = query.data.replace("voice:", "")
        tts = gTTS(text=text, lang='fa')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tts.save(tmp.name)
            await bot.send_audio(chat_id=query.message.chat_id, audio=open(tmp.name, 'rb'))
        await query.edit_message_text("✅ پاسخ صوتی برات فرستادم 🎧")

# ----------------------------------------
# راه‌اندازی اپلیکیشن
# ----------------------------------------
application = Application.builder().token(TOKEN).build()
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
application.add_handler(CallbackQueryHandler(button_handler))

# ----------------------------------------
# اجرای Webhook روی Render
# ----------------------------------------
if __name__ == "__main__":
    hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    if not hostname:
        raise ValueError("❌ متغیر RENDER_EXTERNAL_HOSTNAME پیدا نشد!")
    url = f"https://{hostname}/{TOKEN}"
    print(f"✅ Webhook جدید تنظیم شد: {url}")

    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        url_path=TOKEN,
        webhook_url=url
    )
