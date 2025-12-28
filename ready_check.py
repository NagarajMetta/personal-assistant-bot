#!/usr/bin/env python3
"""Quick test to verify bot is ready for public deployment"""

import requests
import json

BOT_TOKEN = "8363894725:AAFgv8tY5xdd8tGYljdo5998PUKhoAM7IMo"
BOT_URL = "http://127.0.0.1:8000"

print("\n" + "="*60)
print("  BOT READINESS CHECK")
print("="*60)

# Check 1: Bot API is running
print("\n[1/3] Checking if bot API is running...")
try:
    response = requests.get(f"{BOT_URL}/health", timeout=5)
    if response.status_code == 200:
        print("      ✅ Bot API is running at http://127.0.0.1:8000")
    else:
        print(f"      ❌ Bot API returned status {response.status_code}")
except requests.exceptions.ConnectionError:
    print("      ❌ Cannot connect to bot API")
    print("         Run: python main.py")
    exit(1)

# Check 2: Telegram API connection
print("\n[2/3] Checking Telegram API connection...")
try:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
    response = requests.get(url, timeout=5)
    data = response.json()
    if data.get('ok'):
        bot_info = data.get('result', {})
        print(f"      ✅ Connected to Telegram")
        print(f"         Bot: @{bot_info.get('username', '?')}")
        print(f"         ID: {bot_info.get('id', '?')}")
    else:
        print(f"      ❌ {data.get('description', 'Unknown error')}")
except:
    print("      ❌ Cannot connect to Telegram API")

# Check 3: Ngrok status
print("\n[3/3] Checking Ngrok status...")
try:
    response = requests.get('http://127.0.0.1:4040/api/tunnels', timeout=5)
    data = response.json()
    tunnels = data.get('tunnels', [])
    
    https_tunnel = None
    for tunnel in tunnels:
        if tunnel.get('proto') == 'https':
            https_tunnel = tunnel.get('public_url')
            break
    
    if https_tunnel:
        print(f"      ✅ Ngrok is running")
        print(f"         Public URL: {https_tunnel}")
        print(f"         Webhook: {https_tunnel}/telegram/webhook")
        
        # Try to register webhook
        print("\n[BONUS] Auto-registering webhook...")
        webhook_url = f"{https_tunnel}/telegram/webhook"
        register_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
        reg_response = requests.post(register_url, json={"url": webhook_url}, timeout=10)
        reg_data = reg_response.json()
        
        if reg_data.get('ok'):
            print("      ✅ Webhook registered successfully!")
            print(f"\n🎉 YOUR BOT IS NOW PUBLIC!")
            print(f"   Send a message to your bot and it will respond!")
        else:
            print(f"      ⚠️  {reg_data.get('description')}")
    else:
        print("      ❌ Ngrok is not running")
        print("         Run in new terminal: & '$env:LOCALAPPDATA\\ngrok\\ngrok.exe' http 8000")
except:
    print("      ⚠️  Ngrok API not responding")
    print("         Make sure Ngrok is running!")

print("\n" + "="*60)
print("  NEXT STEPS")
print("="*60)
print("\n1. Start Bot:")
print("   python main.py")
print("\n2. Start Ngrok (new terminal):")
print("   & '$env:LOCALAPPDATA\\ngrok\\ngrok.exe' http 8000")
print("\n3. Register webhook (new terminal):")
print("   python ready_check.py")
print("\n4. Test in Telegram:")
print("   Send message to your bot @YourBotName")
print("\n" + "="*60 + "\n")
