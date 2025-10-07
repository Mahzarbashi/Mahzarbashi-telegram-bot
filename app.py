from flask import Flask, request
import requests
import os

app = Flask(__name__)

# توکن واقعی ربات
TOKEN = "8249435097:AAF8PSgEXDVYWYBIXn_q45bHKID_aYDAtqw"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# تست مستقیم API تلگرام
@app.route("/", methods=["GET"])
def index():
    url = f"{BASE_URL}/getMe"
    resp = requests.get(url).json()
    return resp  # اینجا اطلاعات ربات مثل username و id برمی‌گرده

# وبهوک
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            requests.post(f"{BASE_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "سلام 👋 من دستیار محضرباشی هستم 🤖\nبرای پرسیدن سوالات حقوقی می‌تونی همین‌جا پیام بدی."
            })
        else:
            requests.post(f"{BASE_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "دستور ناشناخته. لطفاً /start رو بزن."
            })

    return "ok"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
