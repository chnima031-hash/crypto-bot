import os
import json
import random
import re
import requests

# ==================== تنظیمات ====================
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]

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

# ==================== تولید پست با AI ====================
post_text = None

try:
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "meta-llama/llama-3.3-70b-instruct:free",
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
    
    ai_text = response.json()["choices"][0]["message"]["content"]
    
    # فیلتر کردن خروجی AI
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

except Exception as e:
    print(f"AI Error: {e}")
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
    print("Post sent successfully!")
    
except Exception as e:
    print(f"Telegram Error: {e}")
