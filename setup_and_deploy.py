#!/usr/bin/env python3
"""Complete setup and test script for Ngrok + Telegram webhook"""

import subprocess
import requests
import time
import sys
import os
import json
import platform

def check_ngrok_installed():
    """Check if Ngrok is installed"""
    if platform.system() == "Windows":
        ngrok_path = os.path.expandvars(r"$LOCALAPPDATA\ngrok\ngrok.exe")
    else:
        ngrok_path = os.path.expanduser("~/.ngrok")
    
    return os.path.exists(ngrok_path)

def install_ngrok():
    """Download and install Ngrok"""
    print("\n>>> Downloading Ngrok...")
    
    if platform.system() == "Windows":
        ngrok_dir = os.path.expandvars(r"$LOCALAPPDATA\ngrok")
        download_url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
    else:
        ngrok_dir = os.path.expanduser("~/.ngrok")
        download_url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.zip"
    
    os.makedirs(ngrok_dir, exist_ok=True)
    
    try:
        response = requests.get(download_url, stream=True)
        zip_path = os.path.join(ngrok_dir, "ngrok.zip")
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(">>> Extracting...")
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(ngrok_dir)
        
        os.remove(zip_path)
        print(">>> Ngrok installed!")
        return True
    except Exception as e:
        print(f">>> Error installing Ngrok: {e}")
        return False

def start_ngrok():
    """Start Ngrok"""
    print("\n>>> Starting Ngrok on port 8000...")
    
    if platform.system() == "Windows":
        ngrok_path = os.path.expandvars(r"$LOCALAPPDATA\ngrok\ngrok.exe")
    else:
        ngrok_path = os.path.expanduser("~/.ngrok/ngrok")
    
    try:
        subprocess.Popen([ngrok_path, "http", "8000"], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        print(">>> Ngrok started (running in background)")
        return True
    except Exception as e:
        print(f">>> Error starting Ngrok: {e}")
        return False

def get_ngrok_url():
    """Get the public Ngrok URL"""
    for attempt in range(10):
        try:
            response = requests.get('http://127.0.0.1:4040/api/tunnels', timeout=5)
            data = response.json()
            
            for tunnel in data.get('tunnels', []):
                if tunnel['proto'] == 'https':
                    return tunnel['public_url']
            
            time.sleep(1)
        except:
            time.sleep(1)
    
    return None

def register_webhook(bot_token, webhook_url):
    """Register webhook with Telegram"""
    print(f"\n>>> Registering webhook with Telegram...")
    print(f"    URL: {webhook_url}/telegram/webhook")
    
    url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    payload = {
        "url": f"{webhook_url}/telegram/webhook",
        "allowed_updates": ["message"]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        if result.get('ok'):
            print(">>> Webhook registered successfully!")
            return True
        else:
            print(f">>> Error: {result.get('description')}")
            return False
    except Exception as e:
        print(f">>> Error: {e}")
        return False

def get_webhook_info(bot_token):
    """Get webhook info from Telegram"""
    print("\n>>> Checking webhook status...")
    
    url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
    
    try:
        response = requests.get(url, timeout=10)
        result = response.json()
        
        if result.get('ok'):
            info = result.get('result', {})
            print(f"    Status: {'ACTIVE' if info.get('url') else 'NOT SET'}")
            print(f"    URL: {info.get('url', 'Not set')}")
            print(f"    Pending updates: {info.get('pending_update_count', 0)}")
            return True
        else:
            print(f"    Error: {result.get('description')}")
            return False
    except Exception as e:
        print(f"    Error: {e}")
        return False

def main():
    print("=" * 60)
    print("  TELEGRAM BOT - NGROK SETUP")
    print("=" * 60)
    
    BOT_TOKEN = "8363894725:AAFgv8tY5xdd8tGYljdo5998PUKhoAM7IMo"
    
    # Step 1: Check/Install Ngrok
    print("\n>>> Checking Ngrok...")
    if not check_ngrok_installed():
        print(">>> Ngrok not found, installing...")
        if not install_ngrok():
            print(">>> Installation failed!")
            sys.exit(1)
    else:
        print(">>> Ngrok already installed")
    
    # Step 2: Start Ngrok
    if not start_ngrok():
        sys.exit(1)
    
    time.sleep(2)
    
    # Step 3: Get Ngrok URL
    print("\n>>> Getting Ngrok URL...")
    ngrok_url = get_ngrok_url()
    
    if not ngrok_url:
        print(">>> Failed to get Ngrok URL!")
        print(">>> Make sure Ngrok is running")
        sys.exit(1)
    
    print(f">>> Public URL: {ngrok_url}")
    
    # Step 4: Register webhook
    if not register_webhook(BOT_TOKEN, ngrok_url):
        sys.exit(1)
    
    # Step 5: Verify
    get_webhook_info(BOT_TOKEN)
    
    # Done
    print("\n" + "=" * 60)
    print("  SUCCESS! YOUR BOT IS NOW PUBLIC")
    print("=" * 60)
    print(f"\n>>> Send a message to your bot @YourBotName")
    print(f">>> It will respond in real-time!")
    print(f"\n>>> Public URL: {ngrok_url}")
    print(f">>> Webhook: {ngrok_url}/telegram/webhook")
    print("\n>>> Ngrok is running in the background")
    print(">>> You can close this window, the bot will keep running")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
