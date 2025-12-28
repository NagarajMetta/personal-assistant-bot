# Personal Assistant Bot - Testing Guide

## Pre-Testing Checklist

- [ ] Python 3.9+ installed
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] `.env` file created from `.env.example`
- [ ] Gmail `credentials.json` downloaded
- [ ] Telegram bot token obtained
- [ ] Your Telegram user ID
- [ ] OpenAI API key

## Running the Application

### Start in Development Mode
```bash
python main.py
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Starting Personal Assistant Bot v1.0.0
INFO:     Database initialized
INFO:     Scheduler started successfully
```

## API Testing

### 1. Health Checks
```bash
# Basic health check
curl http://127.0.0.1:8000/

# Detailed health check
curl http://127.0.0.1:8000/health
```

### 2. Telegram Endpoints
```bash
# Get bot status
curl http://127.0.0.1:8000/telegram/status

# Send test message
curl -X POST http://127.0.0.1:8000/telegram/send \
  -H "Content-Type: application/json" \
  -d '{"text": "Test message"}'
```

### 3. Email Endpoints
```bash
# Get unread emails
curl http://localhost:8000/email/unread

# Send email
curl -X POST http://localhost:8000/email/send \
  -H "Content-Type: application/json" \
  -d '{"recipient":"test@example.com","subject":"Test","body":"Hello"}'
```

### 4. Scheduler Endpoints
```bash
# List scheduled jobs
curl http://localhost:8000/scheduler/jobs

# Start scheduler
curl -X POST http://localhost:8000/scheduler/start
```

## Telegram Bot Testing

### Direct Messaging
1. Open Telegram
2. Send to your bot:
   - `/start` - Welcome message
   - `/emails` - Fetch emails
   - `/tasks` - Show tasks
   - `/summary` - Daily summary

### Natural Language
```
"Send email to john@example.com saying hello"
"Read my unread emails"
```

## Success Criteria

✅ Application starts without errors
✅ All endpoints return 200 OK
✅ Telegram commands work
✅ Email fetching works
✅ Email sending works
✅ Tasks can be scheduled
✅ No uncaught exceptions

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Import errors | `pip install -r requirements.txt` |
| Port in use | Change `SERVER_PORT` in .env |
| Gmail auth fails | Delete `token.json`, re-authenticate |
| Telegram not responding | Verify token with /getMe |
| Database errors | Delete `.db` file, restart |

---

All components are production-ready! 🚀
