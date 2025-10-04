import os
from flask import Flask, request
import requests
from gtts import gTTS

# توکن مستقیم اینجا گذاشته شده
TOKEN = "8249435097:AAF8PSgEXDVYWYBIXn_q45bHKID_aYDAtqw"
URL = f"https://api.telegram.org/bot{TOKEN}/"

app = Flask(__name__)

# پاسخ‌های ساده نمونه
def get_reply(text):
    text_lower = text.lower()
    if "طلاق" in text_lower:
        return "طلاق نیاز به بررسی دقیق دارد. برای مشاوره تخصصی به محضرباشی مراجعه کنید: https://mahzarbashi.com"
    elif "سند" in text_lower:
        return "در خصوص اسناد رسمی، طبق قانون مدنی ثبت سند ضروری است."
    else:
        return "سوال شما دریافت شد. اگر عمومی باشد پاسخ می‌دهم، در غیر این صورت به محضرباشی بروید: https://mahzarbashi.com"

# ارسال پیام متنی
def send_message(chat_id, text):
    url = URL + "sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

# ارسال پیام صوتی
def send_voice(chat_id, text):
    tts = gTTS(text=text, lang="fa")
    filename = "voice.ogg"
    tts.save(filename)
    files = {"voice": open(filename, "rb")}
    data = {"chat_id": chat_id}
    requests.post(URL + "sendVoice", data=data, files=files)

@app.route("/", methods=["POST"])
def webhook():
    update = request.get_json()
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")
        reply = get_reply(text)
        send_message(chat_id, reply)
        send_voice(chat_id, reply)
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
