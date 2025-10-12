# app.py (debug version) - جایگزین فایل فعلی کن
import os, sys, traceback
import telegram
import pkgutil

print("=== START DIAGNOSTIC ===")
print("Python sys.version:", sys.version.replace("\n", " "))
try:
    import telegram as tg
    print("python-telegram-bot package found. module path:", tg.__file__)
    try:
        print("telegram.__version__:", getattr(tg, '__version__', 'unknown'))
    except Exception as e:
        print("couldn't read telegram.__version__", e)
except Exception as e:
    print("python-telegram-bot import error:", e)

print("ENV TELEGRAM_TOKEN present?:", "TELEGRAM_TOKEN" in os.environ)
print("TELEGRAM_TOKEN length (masked):", len(os.environ.get("TELEGRAM_TOKEN","")) if "TELEGRAM_TOKEN" in os.environ else "not-set")
print("ENV OPENAI_API_KEY present?:", "OPENAI_API_KEY" in os.environ)
print("OPENAI_API_KEY length (masked):", len(os.environ.get("OPENAI_API_KEY","")) if "OPENAI_API_KEY" in os.environ else "not-set")
print("=== END DIAGNOSTIC ===")

# اگر پایتون نسخه‌ی غیر 3.10 است، متوقف شو و لاگ واضح بفرست
if not sys.version.startswith("3.10"):
    print("\n❗ Detected Python is not 3.10.x — this will cause the Updater error.")
    print("Please ensure runtime.txt exists in repo root with: python-3.10.14")
    sys.exit(1)

# اگر همه چیز خوبه، ادامه بد (در این فایل فقط تست می‌کنیم).
print("Python version is 3.10.x — proceed to real app (you can now replace this file with final app.py).")
