#!/usr/bin/env python3
"""Send a 'Hi' message to the Telegram bot"""

import requests
import time
import random

# Send a simple "Hi" message
test_message = {
    "update_id": random.randint(100000, 999999),
    "message": {
        "message_id": random.randint(1, 100000),
        "date": int(time.time()),
        "text": "Hi",
        "from": {
            "id": 1122501503,
            "is_bot": False,
            "first_name": "User"
        },
        "chat": {
            "id": 1122501503,
            "type": "private"
        }
    }
}

try:
    print("📨 Sending 'Hi' message to bot...")
    response = requests.post(
        "http://127.0.0.1:8000/telegram/webhook",
        json=test_message,
        timeout=5
    )
    
    print(f"✅ Message sent!")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
    
except Exception as e:
    print(f"❌ Error: {e}")
