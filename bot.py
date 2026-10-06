import os
import json
import random
import re
import requests

# ==================== تنظیمات ====================
BOT_TOKEN = os.environ["BOT_TOKEN"].strip()
CHANNEL_ID = os.environ["CHANNEL_ID"].strip()
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"].strip()

# ==================== خواندن بازی‌ها ====================
with open('games.json', 'r', encoding='utf-8') as f:
    GAMES = json.load(f)

game = random.choice(GAMES)

# ==================== پست‌های پیش‌فرض ====================
FALLBACK_POSTS = [
    f"🎮 بازی {game['name']}\n\n{game['description']}\n\n🔥 همین الان شروع کن و توکن رایگان بگیر!\n\n🔗 {game['referral']}\n\n👇 عضو کانال ما شوید",
    f"💰 {game['name']} یکی از بهترین بازی‌های ایردراپیه!\n\n🔥 از لینک زیر شروع کن:\n\n🔗 {game['referral']}",
    f"🔥 {game['name']} رو از دست نده!\n\n{game['description']}\n\n🔗 {game['referral']}",
]

# ==================== لیست مدل‌های جایگزین ====================
MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "meta-llama/llama-4-maverick-17b-128e-instruct",
    "qwen/qwen3.8-27b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]

# ==================== تولید پست با AI (با چند مدل جایگزین) ====================
post_text = None
ai_text = None

for model_name in MODELS:
    try:
        print(f"Trying model: {model_name}")
        response = requests.post(
            url="https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a crypto marketing assistant for a Telegram channel. "
                            "Rules:\n"
                            "1. Write ONLY in Persian.\n"
                            "2. Keep it under 150 words.\n"
                            "3. Use emojis.\n"
                            "4. Write plain text only. No HTML, no markdown, no links.\n"
                            "5. Do NOT make up fake numbers or rewards.\n"
                            "6. Do NOT include any URL.\n"
                            "7. End with a friendly call to action."
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            f"یک پست کوتاه و جذاب درباره بازی {game['name']} بنویس. "
                            f"توضیح بده که {game['description']}. "
                            f"کاربر را تشویق کن که از لینک رفرال شروع کنه. "
                            f"هیچ لینکی توی متن نذار."
                        )
                    }
                ]
            },
            timeout=60
        )
        
        response_json = response.json()
        print(f"Model {model_name} - Status: {response.status_code}")
        
        if "choices" in response_json:
            ai_text = response_json["choices"][0]["message"]["content"]
            print(f"✅ Success with model: {model_name}")
            break
        else:
            print(f"❌ Model {model_name} failed: {response_json}")
            continue
            
    except Exception as e:
        print(f"❌ Model {model_name} error: {e}")
        continue

# ==================== فیلتر کردن خروجی AI ====================
if ai_text:
    ai_text = re.sub(r'http\S+', '', ai_text)
    ai_text = re.sub(r'www\.\S+', '', ai_text)
    
    if len(ai_text) > 1000:
        ai_text = ai_text[:1000]
    
    if not ai_text or len(ai_text) < 30:
        post_text = random.choice(FALLBACK_POSTS)
    else:
        post_text = f"""{ai_text}

🔗 لینک شروع بازی {game['name']}:
{game['referral']}

🎮 عضو کانال ما شوید:
{CHANNEL_ID}
"""
        print("AI Post generated successfully!")
else:
    print("❌ All models failed. Using fallback post.")
    post_text = random.choice(FALLBACK_POSTS)

# ==================== ارسال به تلگرام ====================
try:
    telegram_response = requests.post(
        url=f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHANNEL_ID,
            "text": post_text,
            "disable_web_page_preview": False
        },
        timeout=30
    )
    print(f"Telegram response: {telegram_response.status_code}")
    print(f"Telegram body: {telegram_response.text}")
    
    if telegram_response.status_code == 200:
        print("Post sent successfully!")
    else:
        print(f"Telegram Error: {telegram_response.text}")

except Exception as e:
    print(f"Telegram Error: {e}")
