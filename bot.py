from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

app = Flask(__name__)
flask_app = app  # اضافه کردن این خط خیلی مهمه!

@app.route('/')
def home():
    return "Mahzarbashi Bot is running!"

# ادامه کدهای ربات اینجا...
