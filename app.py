import os
import json
import time
import tempfile
from typing import Optional

import requests
import telebot
from flask import Flask, request, jsonify
from gtts import gTTS

# ----------------------------
# Configuration (do NOT hardcode API keys here)
# ----------------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # set this in Render env
GROQ_API_KEY = os.getenv("GROQ_API_KEY")      # set this in Render env (your Groq key)
PROJECT_URL = os.getenv("RENDER_EXTERNAL_URL")  # Render provides this; used to set webhook
PORT = int(os.getenv("PORT", 10000))

if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN not found in environment variables.")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not found in environment variables. Set it in Render env.")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# Groq OpenAI-compatible endpoint
GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"

# Optional: choose a Groq model (examples: "compound-beta", "mixtral-8x7b", or other available models)
# If unsure, start with "compound-beta" or check your Groq console for allowed model names.
GROQ_MODEL = os.getenv("GROQ_MODEL", "compound-beta")

# ----------------------------
# Helper: call Groq chat completions (OpenAI-compatible)
# returns string or raises Exception
# ----------------------------
def groq_chat_completion(messages, max_tokens=512, temperature=0.7, retries=3, delay=1) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(GROQ_CHAT_URL, headers=headers, json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                # Groq returns OpenAI-compatible shape: data["choices"][0]["message"]["content"]
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0].get("message", {}).get("content")
                    if content is None:
                        # sometimes text field may exist for other compat shapes
                        content = data["choices"][0].get("text")
                    return content.strip() if content else ""
                # If response object uses 'text' or 'output', try alternatives:
                if data.get("text"):
                    return data["text"].strip()
                raise Exception(f"Unexpected Groq response shape: {data}")
            else:
                # include body for debugging
                raise Exception(f"Groq API error: status {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"[groq] attempt {attempt} error: {e}")
            if attempt < retries:
                time.sleep(delay)
            else:
                raise

# ----------------------------
# Helper: produce TTS (gTTS) and return filepath
# ----------------------------
def text_to_speech_fa(text: str) -> Optional[str]:
    try:
        tts = gTTS(text=text, lang="fa")
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(tmp.name)
        return tmp.name
    except Exception as e:
        print("TTS error:", e)
        return None

# ----------------------------
# Flask health + test endpoints
# ----------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "bot": "mahzarbashi"}), 200

@app.route("/test_groq", methods=["GET"])
def test_groq():
    try:
        # quick test conversation
        messages = [{"role": "user", "content": "سلام! یک تست اتصال است."}]
        out = groq_chat_completion(messages, max_tokens=64)
        return jsonify({"ok": True, "reply": out}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ----------------------------
# Telegram webhook receiver (OpenAI-compatible)
# ----------------------------
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    try:
        json_update = request.get_json(force=True)
        update = telebot.types.Update.de_json(json_update)
        bot.process_new_updates([update])
    except Exception as e:
        print("Webhook processing error:", e)
    return "", 200

# ----------------------------
# Telegram message handler
# ----------------------------
@bot.message_handler(commands=["start"])
def handle_start(msg):
    welcome = (
        "سلام 👋 من دستیار حقوقی محضرباشی هستم.\n"
        "می‌تونی سوال حقوقی‌ات رو بپرسی؛ من متن و فایل صوتی جواب میدم."
    )
    bot.send_message(msg.chat.id, welcome)

@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    user_text = message.text or ""
    chat_id = message.chat.id
    print(f"[telegram] received from {chat_id}: {user_text}")

    # build messages for Groq (system + user)
    messages = [
        {"role": "system", "content": "تو یک دستیار حقوقی دوستانه و مختصر به زبان فارسی هستی."},
        {"role": "user", "content": user_text}
    ]

    try:
        reply_text = groq_chat_completion(messages, max_tokens=450, temperature=0.3)
    except Exception as e:
        print("[telegram] groq error:", e)
        reply_text = "متأسفم، خطایی در دریافت پاسخ رخ داد. لطفاً دوباره تلاش کن."

    # send text response (safe)
    try:
        bot.send_message(chat_id, reply_text)
    except Exception as e:
        print("[telegram] send_message error:", e)

    # send voice response (best-effort)
    try:
        voice_path = text_to_speech_fa(reply_text)
        if voice_path:
            with open(voice_path, "rb") as f:
                bot.send_voice(chat_id, f)
            os.remove(voice_path)
    except Exception as e:
        print("[telegram] send_voice error:", e)

# ----------------------------
# On start: set webhook (if running on Render with external URL)
# ----------------------------
def set_webhook_if_needed():
    try:
        # remove any existing webhook first (safe)
        bot.remove_webhook()
    except Exception as e:
        print("remove_webhook:", e)

    try:
        if PROJECT_URL:
            full_url = PROJECT_URL.rstrip("/") + f"/{TELEGRAM_TOKEN}"
            print("Setting webhook to:", full_url)
            res = requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook", json={"url": full_url}, timeout=15)
            print("setWebhook response:", res.status_code, res.text)
        else:
            print("RENDER_EXTERNAL_URL not set; webhook not configured automatically.")
    except Exception as e:
        print("Error setting webhook:", e)

# ----------------------------
# Start Flask app and ensure webhook configured
# ----------------------------
if __name__ == "__main__":
    # On process start, attempt to set webhook (best-effort)
    set_webhook_if_needed()
    print(f"Starting Flask on 0.0.0.0:{PORT}")
    app.run(host="0.0.0.0", port=PORT)
