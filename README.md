# Mahzarbashi Telegram Bot

نسخه‌ای از ربات که از Groq (OpenAI-compatible) استفاده می‌کند و پاسخ متنی + صوتی می‌دهد.

## فایل‌ها
- `app.py` : برنامه اصلی
- `requirements.txt` : وابستگی‌ها

## مراحل سریع نصب (با Git + Vercel)
1. کلون یا ایجاد ریپو در GitHub با نام `Mahzarbashi-telegram-bot`
2. پوش و کامیت فایل‌ها
3. در Vercel پروژه را از ریپو ایمپورت کن.
4. در بخش Environment Variables در Vercel مقادیر زیر را اضافه کن:
   - `TELEGRAM_TOKEN` = توکن ربات تلگرام (مثل `8249...`)
   - `GROQ_API_KEY` = کلید Groq (از کنسول Groq)
   - `PROJECT_URL` = آدرس دامنه Vercel (مثلاً `https://your-app.vercel.app`) — اختیاری
5. Deploy کن.
6. (اگر ست خودکار وبهوک کار نکرد) وبهوک را دستی ست کن:
