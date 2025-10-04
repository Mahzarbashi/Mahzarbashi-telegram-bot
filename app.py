from flask import Flask, request
import requests

TOKEN = "8249435097:AAF8PSgEXDVYWYBIXn_q45bHKID_aYDAtqw"
URL = f"https://api.telegram.org/bot{TOKEN}/"

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        if text:
            send_message(chat_id, f"📌 شما نوشتید:\n{text}")
    return "ok", 200

def send_message(chat_id, text):
    url = URL + "sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

@app.route('/')
def home():
    return "Bot is running!", 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
