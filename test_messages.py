#!/usr/bin/env python3
"""Send various test messages to the Telegram bot"""

import requests
import time
import random

def send_message(text):
    """Send a message to the bot"""
    message = {
        "update_id": random.randint(100000, 999999),
        "message": {
            "message_id": random.randint(1, 100000),
            "date": int(time.time()),
            "text": text,
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
        response = requests.post(
            "http://127.0.0.1:8000/telegram/webhook",
            json=message,
            timeout=10
        )
        print(f"✅ '{text}' - Status: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ '{text}' - Error: {e}")
        return False

# Test various messages
messages = [
    "Hello",
    "What time is it?",
    "Send an email to john@example.com",
    "Schedule a meeting tomorrow at 10am",
    "Read my emails",
]

print("📨 Testing bot with various messages...\n")
for msg in messages:
    send_message(msg)
    time.sleep(2)

print("\n✅ All messages sent!")
