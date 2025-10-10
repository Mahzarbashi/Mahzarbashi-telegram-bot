import os
import telebot
import openai

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

BASE_PROMPT = """شما دستیار حقوقی سایت محضرباشی هستید.
لحن شما رسمی، روشن و حرفه‌ای است.
اگر سؤال خیلی تخصصی یا نیاز به وکیل داشت، کاربر را به سایت www.mahzarbashi.ir هدایت کنید.
"""

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_text = message.text

    # دریافت پاسخ متنی از GPT
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": BASE_PROMPT},
            {"role": "user", "content": user_text}
        ]
    )
    answer = response.choices[0].message.content.strip()

    # ارسال پاسخ متنی
    bot.reply_to(message, answer)

    # تبدیل پاسخ به صوت با OpenAI TTS
    speech_file = "reply.ogg"
    with open(speech_file, "wb") as f:
        audio_response = openai.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",  # صدای حرفه‌ای
            input=answer
        )
        f.write(audio_response.read())

    with open(speech_file, "rb") as audio:
        bot.send_voice(message.chat.id, audio)

bot.infinity_polling()
