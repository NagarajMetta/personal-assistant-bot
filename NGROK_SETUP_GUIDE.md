# PUBLIC BOT SETUP - Quick Guide

## Step 1: Start Your Bot
Open a terminal and run:
```powershell
cd d:\AI\Bot
python main.py
```
Wait until you see: `Application startup complete`

## Step 2: Start Ngrok
Open a NEW terminal and run:
```powershell
cd d:\AI\Bot
.\start_ngrok.ps1
```

You'll see output like:
```
Session Status                online
Forwarding                    https://abc123def456.ngrok.io -> http://127.0.0.1:8000
```

COPY the `https://abc123def456.ngrok.io` URL (your URL will be different)

## Step 3: Register Webhook With Telegram
Open a NEW terminal and run:
```powershell
cd d:\AI\Bot
python register_webhook.py
```

This will:
- Auto-detect your Ngrok URL
- Register it with Telegram
- Show you the status

Expected output:
```
Registering webhook with Telegram...
   URL: https://abc123def456.ngrok.io/telegram/webhook
Webhook registered successfully!

Webhook Information:
   Status: Active
   URL: https://abc123def456.ngrok.io/telegram/webhook
```

## Step 4: Test It!
Open Telegram and:
1. Find your bot @YourBotName
2. Send a message like: "Hello"
3. Bot should respond in real-time!

## Important Notes

- **Ngrok URL changes every restart** - You'll need to re-run `register_webhook.py` after restarting Ngrok
- **Free Ngrok** - Works but expires after 2 hours of no activity. Pro plan ($5/month) for unlimited

## Troubleshooting

### Bot not responding?
1. Check Terminal 1: Bot should be running (`Application startup complete`)
2. Check Terminal 2: Ngrok should show `Session Status: online`
3. Check Terminal 3: `register_webhook.py` should show `Status: Active`

### Webhook shows inactive?
1. Stop Ngrok (press CTRL+C in Terminal 2)
2. Start Ngrok again: `.\start_ngrok.ps1`
3. Register webhook again: `python register_webhook.py`

### Need to use a custom domain instead of Ngrok?
Edit `register_webhook.py` and manually pass your domain:
```powershell
python register_webhook.py --url https://yourdomain.com
```

## Next Steps (Production)

For a permanent solution without Ngrok limitations:
- Deploy to **Railway.app** ($5/month)
- Use **DigitalOcean** ($4-6/month)
- Run on **your own VPS** with a domain

Let me know if you want help with any of these!
