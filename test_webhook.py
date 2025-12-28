#!/usr/bin/env python3
"""Test webhook endpoint with unique message IDs"""

import requests
import json
import sys
import uuid

url = 'http://127.0.0.1:8000/telegram/webhook'

# Create unique message ID  
unique_id = str(uuid.uuid4())[:8]

payload = {
    'update_id': int(uuid.uuid4().int % 1000000),
    'message': {
        'message_id': int(uuid.uuid4().int % 1000000),
        'date': 1234567890,
        'chat': {'id': 1122501503},
        'from': {'id': 1122501503},
        'text': f'Hello, how are you? ({unique_id})'
    }
}

try:
    print(f'Sending test message with ID: {unique_id}...')
    response = requests.post(url, json=payload, timeout=10)
    print(f'Webhook Status Code: {response.status_code}')
    print(f'Webhook Response: {response.text}')
    
    if response.status_code == 200:
        print('\n✅ Message was processed successfully!')
        print('✅ Bot processed the message and sent a response to Telegram!')
    else:
        print(f'\n❌ Error processing message')
    
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')
    sys.exit(1)
