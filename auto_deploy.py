import requests
import time
import sys

print("Waiting for Ngrok to start...")

for attempt in range(20):
    try:
        response = requests.get('http://127.0.0.1:4040/api/tunnels', timeout=3)
        data = response.json()
        tunnels = data.get('tunnels', [])
        
        for tunnel in tunnels:
            if tunnel.get('proto') == 'https':
                url = tunnel.get('public_url')
                print(f'\nNgrok URL: {url}')
                
                BOT_TOKEN = '8363894725:AAFgv8tY5xdd8tGYljdo5998PUKhoAM7IMo'
                webhook_url = f'{url}/telegram/webhook'
                reg_url = f'https://api.telegram.org/bot{BOT_TOKEN}/setWebhook'
                
                reg_response = requests.post(reg_url, json={'url': webhook_url}, timeout=10)
                reg_data = reg_response.json()
                
                if reg_data.get('ok'):
                    print('✅ Webhook registered successfully!')
                    print(f'📍 Webhook URL: {webhook_url}')
                    print('\n🎉 YOUR BOT IS NOW LIVE!')
                    print('\nOpen Telegram and send a message to @Aryan2021_bot')
                    print('It will respond in real-time!')
                    sys.exit(0)
                else:
                    print(f'Error: {reg_data.get("description")}')
                    sys.exit(1)
        
        print(".", end="", flush=True)
        time.sleep(1)
    except Exception as e:
        print(".", end="", flush=True)
        time.sleep(1)

print('\nNgrok not responding - check if it started')
