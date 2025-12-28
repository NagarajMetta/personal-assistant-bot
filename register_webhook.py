#!/usr/bin/env python3
"""Register Telegram webhook with Ngrok URL"""

import requests
import sys
import re

# Your bot credentials
BOT_TOKEN = "8363894725:AAFgv8tY5xdd8tGYljdo5998PUKhoAM7IMo"

def get_ngrok_url():
    """Get the public Ngrok URL from the API"""
    try:
        response = requests.get('http://127.0.0.1:4040/api/tunnels', timeout=5)
        data = response.json()
        
        for tunnel in data.get('tunnels', []):
            if tunnel['proto'] == 'https':
                return tunnel['public_url']
        
        return None
    except:
        return None

def register_webhook(webhook_url):
    """Register webhook with Telegram"""
    print(f"\n📍 Registering webhook with Telegram...")
    print(f"   URL: {webhook_url}/telegram/webhook")
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    payload = {
        "url": f"{webhook_url}/telegram/webhook",
        "allowed_updates": ["message"]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        if result.get('ok'):
            print(f"✅ Webhook registered successfully!\n")
            return True
        else:
            print(f"❌ Failed to register: {result.get('description')}\n")
            return False
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return False

def get_webhook_info():
    """Get webhook info from Telegram"""
    print("📊 Webhook Information:")
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
    
    try:
        response = requests.get(url, timeout=10)
        result = response.json()
        
        if result.get('ok'):
            info = result.get('result', {})
            print(f"   Status: {'✅ Active' if info.get('url') else '❌ Not set'}")
            print(f"   URL: {info.get('url', 'Not set')}")
            print(f"   Has custom certificate: {info.get('has_custom_certificate', False)}")
            print(f"   Pending update count: {info.get('pending_update_count', 0)}")
            print()
            return True
        else:
            print(f"   Error: {result.get('description')}\n")
            return False
    except Exception as e:
        print(f"   Error: {e}\n")
        return False

def main():
    print("=" * 50)
    print("  TELEGRAM WEBHOOK REGISTRATION")
    print("=" * 50)
    
    # Get Ngrok URL
    print("\n🔍 Looking for Ngrok URL...")
    ngrok_url = get_ngrok_url()
    
    if ngrok_url:
        print(f"✅ Found Ngrok URL: {ngrok_url}")
        
        # Register webhook
        if register_webhook(ngrok_url):
            # Show webhook info
            get_webhook_info()
            
            print("=" * 50)
            print("✅ YOUR BOT IS NOW PUBLIC!")
            print("=" * 50)
            print(f"\n📱 Send a message to your bot @YourBotName")
            print(f"   It should respond in real-time!\n")
        else:
            print("Failed to register webhook")
            sys.exit(1)
    else:
        print("❌ Could not find Ngrok URL")
        print("\n⚠️  Make sure Ngrok is running:")
        print("   In another terminal, run: .\\start_ngrok.ps1")
        print("\nOr manually provide the Ngrok URL:")
        webhook = input("\nEnter your Ngrok URL (e.g., https://abc123.ngrok.io): ").strip()
        
        if webhook:
            if register_webhook(webhook):
                get_webhook_info()
                print("=" * 50)
                print("✅ YOUR BOT IS NOW PUBLIC!")
                print("=" * 50)
            else:
                sys.exit(1)
        else:
            print("No URL provided")
            sys.exit(1)

if __name__ == "__main__":
    main()
