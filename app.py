import os
from flask import Flask, request
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import openai
from gtts import gTTS

# ---- تنظیم کلیدها ----
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise ValueError("❌ TELEGRAM_TOKEN یا OPENAI_API_KEY پیدا نشد. لطفاً Environment Variables را در Render چک کنید.")

openai.api_key = OPENAI_API_KEY
bot = Bot(token=TELEGRAM_TOKEN)
app = Flask(__name__)
application = Application.builder().token(TELEGRAM_TOKEN).build()

# ---- دکمه‌ها ----
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👩‍❤️‍👨 خانواده", callback_data="cat_family")],
        [InlineKeyboardButton("💼 قراردادها", callback_data="cat_contracts")],
        [InlineKeyboardButton("💳 اسناد و چک", callback_data="cat_cheque")],
        [InlineKeyboardButton("🏛 کیفری و شکایت", callback_data="cat_criminal")],
        [InlineKeyboardButton("🏠 ملکی و اجاره", callback_data="cat_property")],
        [InlineKeyboardButton("🌐 سایت محضرباشی", url="https://www.mahzarbashi.ir")]
    ])

# ---- متون FAQ آماده ----
faq_texts = {
    "faq_mehrieh": "📌 *مهریه*: زن هر زمان بخواهد می‌تواند مهریه‌اش را مطالبه کند. اجرای مهریه از طریق دادگاه یا اجرای ثبت امکان‌پذیر است.",
    "faq_talagh": "📌 *طلاق*: برای طلاق توافقی، زوجین باید در دادگاه حضور یافته و درباره مهریه، حضانت و جهیزیه توافق کنند.",
    "faq_hazanat": "📌 *حضانت فرزند*: حضانت تا ۷ سالگی با مادر و پس از آن با پدر است، مگر آن‌که دادگاه مصلحت طفل را خلاف آن بداند.",
    "faq_contract": "📌 *قرارداد*: همیشه قرارداد را مکتوب و با تاریخ دقیق بنویسید. شاهد و امضا فراموش نشود.",
    "faq_faskh": "📌 *فسخ قرارداد*: در صورتی که یکی از طرفین به تعهدات خود عمل نکند، حق فسخ وجود دارد.",
    "faq_delay": "📌 *خسارت تأخیر*: در قراردادها می‌توانید شرط خسارت تأخیر درج کنید تا طرف مقابل در زمان تأخیر مسئول پرداخت باشد.",
    "faq_cheque": "📌 *چک برگشتی*: پس از گواهی عدم پرداخت، دارنده چک می‌تواند از طریق دادگاه یا اجرای ثبت اقدام کند.",
    "faq_safte": "📌 *سفته*: باید مبلغ، تاریخ و امضا مشخص باشد. در صورت عدم پرداخت، می‌توان از طریق دادگاه اقدام کرد.",
    "faq_criminal": "📌 *شکایت کیفری*: شامل جرایمی مثل سرقت، تهدید، کلاهبرداری و ... است و باید در دادسرا مطرح شود.",
    "faq_tohin": "📌 *توهین و تهدید*: جرم است و با ارائه مدارک (پیام، شاهد و ...) در دادسرا قابل پیگیری است.",
    "faq_mozahmet": "📌 *مزاحمت تلفنی*: با شماره‌گیری ۱۱۰ و گزارش به پلیس فتا می‌توان پیگیری کرد.",
    "faq_ejare": "📌 *اجاره‌نامه*: قرارداد باید کتبی و با ذکر مدت و مبلغ تنظیم شود تا معتبر باشد.",
    "faq_khl": "📌 *خلع ید*: یعنی تخلیه ملک از تصرف غیرقانونی، که با حکم دادگاه انجام می‌شود.",
    "faq_mobaye": "📌 *مبایعه‌نامه*: سند خرید و فروش ملک است و باید در دفتر املاک معتبر تنظیم شود."
}

# ---- /start ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! 👋\nمن ربات *محضرباشی* هستم.\n"
        "می‌تونی یکی از دسته‌های زیر رو انتخاب کنی یا سوال حقوقی‌ات رو بنویسی:",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

# ---- Callback برای دسته‌ها ----
async def faq_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    buttons = []
    reply_text = ""

    if data == "cat_family":
        reply_text = "موضوعات خانواده را انتخاب کنید:"
        buttons = [
            [InlineKeyboardButton("👰 مهریه", callback_data="faq_mehrieh")],
            [InlineKeyboardButton("💔 طلاق", callback_data="faq_talagh")],
            [InlineKeyboardButton("👶 حضانت فرزند", callback_data="faq_hazanat")],
            [InlineKeyboardButton("بازگشت به منوی اصلی ⬅️", callback_data="main_menu")]
        ]
    elif data == "cat_contracts":
        reply_text = "موضوعات قراردادها را انتخاب کنید:"
        buttons = [
            [InlineKeyboardButton("✍️ تنظیم قرارداد", callback_data="faq_contract")],
            [InlineKeyboardButton("📄 فسخ قرارداد", callback_data="faq_faskh")],
            [InlineKeyboardButton("⚖️ خسارت تأخیر", callback_data="faq_delay")],
            [InlineKeyboardButton("بازگشت به منوی اصلی ⬅️", callback_data="main_menu")]
        ]
    elif data == "cat_cheque":
        reply_text = "موضوعات مربوط به چک و سفته:"
        buttons = [
            [InlineKeyboardButton("💳 چک برگشتی", callback_data="faq_cheque")],
            [InlineKeyboardButton("📜 سفته", callback_data="faq_safte")],
            [InlineKeyboardButton("بازگشت به منوی اصلی ⬅️", callback_data="main_menu")]
        ]
    elif data == "cat_criminal":
        reply_text = "موضوعات کیفری:"
        buttons = [
            [InlineKeyboardButton("🚨 شکایت کیفری", callback_data="faq_criminal")],
            [InlineKeyboardButton("👮‍♂️ توهین و تهدید", callback_data="faq_tohin")],
            [InlineKeyboardButton("📵 مزاحمت تلفنی", callback_data="faq_mozahmet")],
            [InlineKeyboardButton("بازگشت به منوی اصلی ⬅️", callback_data="main_menu")]
        ]
    elif data == "cat_property":
        reply_text = "موضوعات ملکی:"
        buttons = [
            [InlineKeyboardButton("🏠 اجاره‌نامه", callback_data="faq_ejare")],
            [InlineKeyboardButton("🏗 خلع ید", callback_data="faq_khl")],
            [InlineKeyboardButton("🧾 مبایعه‌نامه", callback_data="faq_mobaye")],
            [InlineKeyboardButton("بازگشت به منوی اصلی ⬅️", callback_data="main_menu")]
        ]
    elif data == "main_menu":
        await query.message.reply_text("بازگشت به منوی اصلی:", reply_markup=main_menu())
        return

    if buttons:
        await query.message.reply_text(reply_text, reply_markup=InlineKeyboardMarkup(buttons))
        return

    # پاسخ به هر FAQ
    if data in faq_texts:
        reply_text = faq_texts[data]
        await query.message.reply_text(reply_text, parse_mode="Markdown")
        tts = gTTS(text=reply_text, lang='fa')
        audio_path = f"voice_{query.id}.mp3"
        tts.save(audio_path)
        with open(audio_path, 'rb') as audio_file:
            await query.message.reply_voice(audio_file)
        os.remove(audio_path)

# ---- پاسخ به پیام‌ها با تشخیص کلمات کلیدی FAQ ----
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    faq_keywords = {
        "مهریه": "faq_mehrieh",
        "طلاق": "faq_talagh",
        "حضانت": "faq_hazanat",
        "قرارداد": "faq_contract",
        "فسخ قرارداد": "faq_faskh",
        "خسارت": "faq_delay",
        "چک": "faq_cheque",
        "سفته": "faq_safte",
        "شکایت کیفری": "faq_criminal",
        "توهین": "faq_tohin",
        "مزاحمت": "faq_mozahmet",
        "اجاره": "faq_ejare",
        "خلع ید": "faq_khl",
        "مبایعه‌نامه": "faq_mobaye"
    }
