import os
import openai

# -------------------------
# Environment Variables
# -------------------------
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise Exception("OPENAI_API_KEY در Environment Variables ست نشده است!")

openai.api_key = OPENAI_API_KEY

# -------------------------
# تست اتصال به OpenAI
# -------------------------
try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "سلام! فقط یک تست اتصال به OpenAI است."}],
        max_tokens=50
    )
    print("✅ اتصال موفق! پاسخ OpenAI:")
    print(response.choices[0].message.content.strip())
except Exception as e:
    print("❌ خطای OpenAI:", e)
