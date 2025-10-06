from flask import Flask, request
import requests
import os

app = Flask(__name__)

# توکن ربات تلگرام
TOKEN = "8249435097:AAF8PSgEXDVYWYBIXn_q45bHKID_aYDAtqw"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        if text == "/start":
            send_message(chat_id, "سلام! من دستیار محضرباشی هستم 🤖\nبرای دریافت راهنمایی حقوقی پیام بده.")
        else:
            send_message(chat_id, "متاسفم، این دستور را نمی‌شناسم. لطفا /start را امتحان کنید.")
    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
