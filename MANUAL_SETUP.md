# SETUP YOUR PUBLIC BOT - MANUAL STEPS

## ✅ What We've Done For You

1. ✅ Installed Ngrok
2. ✅ Created setup scripts
3. ✅ Your bot works locally (tested and confirmed!)
4. ✅ Created webhook registration script

## 🚀 Manual Setup (3 Easy Steps)

### Step 1: Start Your Bot
Open PowerShell and run:
```powershell
cd d:\AI\Bot
python main.py
```
Wait for: `Application startup complete`

### Step 2: Start Ngrok
Open a NEW PowerShell and run:
```powershell
$ngrokPath = "$env:LOCALAPPDATA\ngrok\ngrok.exe"
& $ngrokPath http 8000
```

You should see:
```
Session Status      online
Forwarding          https://abc123def456.ngrok.io -> http://127.0.0.1:8000
Web Interface       http://127.0.0.1:4040
```

**COPY the `https://abc123def456.ngrok.io` URL**

### Step 3: Register Webhook
Open a THIRD PowerShell and run:
```powershell
cd d:\AI\Bot

$BOT_TOKEN = "8363894725:AAFgv8tY5xdd8tGYljdo5998PUKhoAM7IMo"
$NGROK_URL = "https://your-url-from-step2.ngrok.io"
$WEBHOOK_URL = "$NGROK_URL/telegram/webhook"

Invoke-WebRequest `
  -Uri "https://api.telegram.org/bot$BOT_TOKEN/setWebhook" `
  -Method Post `
  -Body @{url=$WEBHOOK_URL} `
  -ContentType "application/x-www-form-urlencoded"
```

## ✅ Success!

If you see in PowerShell:
```json
{"ok":true,"result":{"url":"...","has_custom_certificate":false,"pending_update_count":0}}
```

Then open Telegram, find your bot @YourBotName and send a message!

## 📱 Test It

1. Open Telegram app
2. Search for your bot @YourBotName (ask BotFather what your bot's username is)
3. Send: "Hello"
4. Bot should respond in real-time!

## ⚠️ Important

- **Ngrok URL changes every restart** → Need to re-run Step 3
- **Free Ngrok limit** → 2 hours, then restarts. Pro plan ($5/month) for unlimited
- **Keep all 3 terminals open** → Bot, Ngrok, and verification

## 🔧 Troubleshooting

### "Bot not responding"?
1. Check PowerShell 1: Bot running? Should see `Application startup complete`
2. Check PowerShell 2: Ngrok shows `Session Status: online`?
3. Check PowerShell 3: Webhook registered? Look for `"ok":true`

### "Ngrok keeps restarting"?
- Upgrade to Pro ($5/month): https://ngrok.com/pricing

### "Webhook says inactive"?
1. Kill Ngrok (Ctrl+C in terminal 2)
2. Restart Ngrok: `& $ngrokPath http 8000`
3. Re-register webhook in terminal 3

## 🎯 Next: Production Setup

For permanent, no-hassle hosting:
- **Railway.app** ($5/month) - Easiest
- **DigitalOcean** ($4-6/month) - More control
- **Your own VPS** - Full control

Ask if you want help with any of these!
