# Personal Assistant Bot - Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Set Up Gmail API
1. Visit https://console.cloud.google.com/
2. Create new project → Enable Gmail API
3. Create OAuth 2.0 credentials (Desktop) → Download as `credentials.json`
4. Place `credentials.json` in project root

### Step 3: Get Telegram Bot Token
1. Message @BotFather on Telegram
2. Create new bot with `/newbot`
3. Copy the token

### Step 4: Get Your Telegram User ID
1. Message @userinfobot on Telegram
2. It will show your user ID

### Step 5: Get OpenAI API Key
1. Visit https://platform.openai.com/api-keys
2. Create new API key
3. Copy it (keep it secret!)

### Step 6: Configure Environment
```bash
cp .env.example .env
```

Edit `.env` and fill in:
```env
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_USER_ID=your_user_id
OPENAI_API_KEY=your_openai_key
```

### Step 7: Run the Bot
```bash
python main.py
```

Visit http://127.0.0.1:8000/docs to see the API

## Project Structure Overview

```
Bot/
├── main.py                    ← Start here
├── app/
│   ├── config.py             ← Settings & environment
│   ├── services/             ← Gmail, Telegram, OpenAI
│   ├── routers/              ← API endpoints
│   ├── models/               ← Database & schemas
│   └── workers/              ← Background tasks
├── requirements.txt          ← Dependencies
├── .env                       ← Your secrets (create from example)
└── README.md                  ← Full documentation
```

## Basic Usage

### Via Telegram
Send messages to your bot:
- `/emails` - Read unread emails
- `/tasks` - Show pending tasks
- `/summary` - Get daily summary
- `/help` - Show help

Or use natural language:
- "Send an email to john@example.com saying hello"
- "Read my unread emails"

### Via API
```bash
# Get unread emails
curl http://localhost:8000/email/unread

# Send an email
curl -X POST http://localhost:8000/email/send \
  -H "Content-Type: application/json" \
  -d '{"recipient":"user@example.com","subject":"Hi","body":"Hello"}'

# Schedule a task
curl -X POST http://localhost:8000/scheduler/schedule \
  -H "Content-Type: application/json" \
  -d '{"task_name":"Morning","command":"check_emails","schedule_time":"08:00","job_type":"daily"}'
```

## Key Features Already Implemented

✅ **Gmail Integration**
- Read unread emails with AI summarization
- Send emails via Telegram commands
- Priority classification (low/medium/high/urgent)

✅ **Telegram Bot**
- Natural language command parsing
- Slash commands (/emails, /tasks, etc.)
- Rich message formatting with emojis

✅ **Task Scheduler**
- Daily/weekly recurring tasks
- One-time scheduled tasks
- Job management (pause, resume, delete)

✅ **AI Features**
- Command parsing with OpenAI
- Email summarization
- Auto-reply generation
- Daily summary generation

✅ **Database**
- SQLite with SQLAlchemy
- Models for tasks, emails, messages
- Automatic initialization

## Common Tasks

### Schedule Morning Summary at 8 AM
```bash
curl -X POST http://localhost:8000/scheduler/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "Morning Summary",
    "command": "send_morning_summary",
    "schedule_time": "08:00",
    "job_type": "daily"
  }'
```

### Get List of Scheduled Jobs
```bash
curl http://localhost:8000/scheduler/jobs
```

### Read Emails with AI Summary
```bash
curl http://localhost:8000/email/unread?limit=5
```

## Next Steps

1. **Customize commands** in `app/routers/telegram.py`
2. **Add email rules** in `app/workers/tasks.py`
3. **Modify schedules** in `.env` and API calls
4. **Extend with more services** (Calendar, Notion, etc.)

## Troubleshooting

**Bot not responding to messages?**
- Check TELEGRAM_TOKEN in .env
- Verify TELEGRAM_USER_ID is correct
- Check logs in console

**Gmail not working?**
- Delete `token.json` to force re-authentication
- Verify Gmail API is enabled in Google Cloud
- Check credentials.json exists

**Scheduler not running?**
- Set `SCHEDULER_ENABLED=True` in .env
- Check logs for scheduler errors
- Restart the application

## Documentation

- Full README: See `README.md`
- API Docs: http://127.0.0.1:8000/docs (Swagger)
- Code Documentation: Inline docstrings in all files

## Support

For detailed information, see `README.md` in the project root.

Happy automating! 🤖
