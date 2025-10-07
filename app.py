from flask import Flask, request
import requests
import os
from gtts import gTTS  # برای تولید صوت

app = Flask(__name__)

# توکن ربات
TOKEN = "8249435097:AAF8PSgEXDVYWYBIXn_q45bHKID_aYDAtqw"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# تابع ارسال متن
def send_message(chat_id, text, keyboard=None):
    payload = {"chat_id": chat_id, "text": text}
    if keyboard:
        payload["reply_markup"] = keyboard
    requests.post(f"{BASE_URL}/sendMessage", json=payload)

# تابع ارسال صوت
def send_voice(chat_id, text):
    try:
        tts = gTTS(text=text, lang="fa")
        tts.save("voice.ogg")
        with open("voice.ogg", "rb") as f:
            requests.post(f"{BASE_URL}/sendVoice", data={"chat_id": chat_id}, files={"voice": f})
    except Exception as e:
        print("Voice error:", e)

@app.route("/", methods=["GET"])
def index():
    return {"status": "ok", "bot": "Mahzarbashi Assistant"}

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            keyboard = {
                "keyboard": [
                    [{"text": "📑 قراردادها"}, {"text": "⚖️ دعاوی حقوقی"}],
                    [{"text": "🏛️ دفترخانه و محضر"}, {"text": "🌐 سایت محضرباشی"}]
                ],
                "resize_keyboard": True
            }
            msg = "سلام 👋\nمن دستیار محضرباشی هستم.\nمی‌تونم راهنمایی‌های حقوقی ساده بدم و برای سوالات تخصصی شما رو به سایت محضرباشی هدایت کنم."
            send_message(chat_id, msg, keyboard)
            send_voice(chat_id, msg)

        elif text == "📑 قراردادها":
            msg = "برای نمونه قراردادها به سایت مراجعه کنید: www.mahzarbashi.ir/contracts"
            send_message(chat_id, msg)
            send_voice(chat_id, msg)

        elif text == "⚖️ دعاوی حقوقی":
            msg = "برای دعاوی حقوقی جزئیات بیشتر در سایت موجود است: www.mahzarbashi.ir/lawsuits"
            send_message(chat_id, msg)
            send_voice(chat_id, msg)

        elif text == "🏛️ دفترخانه و محضر":
            msg = "سوالات رایج دفترخانه و محضر: www.mahzarbashi.ir/notary"
            send_message(chat_id, msg)
            send_voice(chat_id, msg)

        elif text == "🌐 سایت محضرباشی":
            msg = "برای مشاوره تخصصی وارد سایت شوید: www.mahzarbashi.ir"
            send_message(chat_id, msg)
            send_voice(chat_id, msg)

        else:
            msg = "متوجه نشدم. لطفاً از منوی پایین انتخاب کنید یا وارد سایت شوید: www.mahzarbashi.ir"
            send_message(chat_id, msg)
            send_voice(chat_id, msg)

    return "ok"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
