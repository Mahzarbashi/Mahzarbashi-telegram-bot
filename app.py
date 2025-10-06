from flask import Flask, request
import requests

TOKEN = "8249435097:AAF8PSgEXDVYWYBIXn_q45bHKID_aYDAtqw"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

@app.route('/')
def home():
    return "ربات محضرباشی زنده است ✅"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_message(chat_id, "سلام 👋 به ربات محضرباشی خوش آمدید.\nلطفاً سوال خود را بپرسید.")
        else:
            send_message(chat_id, f"شما گفتید: {text}")

    return {"ok": True}

def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
