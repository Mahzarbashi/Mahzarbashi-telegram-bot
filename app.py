from flask import Flask, request
import telebot
import requests
import os

# Token های محیطی
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Mahzarbashi Telegram Bot is live on Vercel!"

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def receive_update():
    json_update = request.get_json(force=True)
    bot.process_new_updates([telebot.types.Update.de_json(json_update)])
    return "OK", 200

@bot.message_handler(func=lambda message: True)
def reply_all(message):
    bot.reply_to(message, "سلام! ربات محضرباشی آماده پاسخ‌گویی است 💬")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
