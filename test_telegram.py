#!/usr/bin/env python3
"""Test script to send messages to the Telegram bot webhook"""

import requests
import json
import time
import random

# Wait for bot to be ready
time.sleep(1)

# Test message payload with unique message ID
test_message = {
    "update_id": 123456789 + random.randint(1, 10000),
    "message": {
        "message_id": random.randint(1, 10000),
        "date": int(time.time()),
        "text": "Hello bot! This is a test message from Copilot.",
        "from": {
            "id": 1122501503,
            "is_bot": False,
            "first_name": "Test User"
        },
        "chat": {
            "id": 1122501503,
            "type": "private"
        }
    }
}

try:
    print(f"📨 Sending test message to bot...")
    print(f"   Message ID: {test_message['message']['message_id']}")
    print(f"   Text: {test_message['message']['text']}")
    
    response = requests.post(
        "http://127.0.0.1:8000/telegram/webhook",
        json=test_message,
        timeout=5
    )
    print(f"\n📊 Status Code: {response.status_code}")
    print(f"📄 Response: {response.text[:200]}...")
    
    if response.status_code == 200:
        print("\n✅ Message sent successfully!")
        print("Bot received and processed the message.")
    else:
        print(f"\n⚠️ Error: HTTP {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")
