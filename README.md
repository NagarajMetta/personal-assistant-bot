# Personal Assistant Bot

A powerful, AI-driven personal assistant bot that automates daily tasks including email management, message scheduling, and task automation using FastAPI, Gmail API, Telegram Bot API, and OpenAI.

## Features

### 📧 Email Assistant
- **Read Unread Emails**: Fetch and display unread emails from Gmail
- **Email Summarization**: Use AI to automatically summarize email content
- **Email Priority Classification**: Automatically classify emails by priority (low, medium, high, urgent)
- **Send Emails**: Send emails with attachments via Telegram commands
- **Draft Management**: Create and save email drafts
- **Auto-Reply**: Generate smart replies based on email content

### 💬 Telegram Bot
- **Natural Language Commands**: Understand and execute commands in natural language
- **Command Interface**: Slash commands for quick actions (/emails, /tasks, /summary, etc.)
- **Real-time Notifications**: Receive email summaries and task updates via Telegram
- **Message Formatting**: HTML-formatted messages with emojis and rich content

### 🕐 Task Scheduler
- **Daily Routines**: Morning and evening summaries with customizable times
- **One-time Tasks**: Schedule tasks for specific dates and times
- **Recurring Tasks**: Set up daily, weekly, or custom cron-based schedules
- **Task Management**: Create, list, pause, resume, and delete scheduled tasks
- **Job Monitoring**: Track scheduled jobs and their execution status

### 🤖 AI-Powered Features
- **Intent Parsing**: Parse natural language to understand user intent
- **Smart Summarization**: Generate concise summaries of emails and documents
- **Command Generation**: Auto-generate appropriate responses and actions
- **Daily Summaries**: Create personalized daily summary reports

### 🔐 Security
- **OAuth2 Authentication**: Secure Gmail API access with OAuth2
- **Token Management**: Automatic token refresh and validation
- **Environment Variables**: All secrets stored securely in .env file
- **Webhook Validation**: Telegram webhook signature verification

## Architecture

```
Bot/
├── main.py                          # FastAPI app entry point
├── requirements.txt                 # All dependencies
├── .env.example                     # Configuration template
├── .gitignore                       # Git ignore rules
├── README.md                        # Full documentation
├── QUICKSTART.md                    # 5-minute setup
├── IMPLEMENTATION.md                # Technical guide
├── EXAMPLES.md                      # Usage examples
└── app/
    ├── __init__.py
    ├── config.py                    # Configuration and settings
    ├── utils.py                     # Helper functions
    ├── models/
    │   ├── __init__.py
    │   ├── database.py              # SQLAlchemy models
    │   └── schemas.py               # Pydantic schemas
    ├── services/
    │   ├── __init__.py
    │   ├── gmail_service.py         # Gmail API client
    │   ├── telegram_service.py      # Telegram bot service
    │   └── ai_service.py            # OpenAI integration
    ├── routers/
    │   ├── __init__.py
    │   ├── telegram.py              # Telegram endpoints
    │   ├── email.py                 # Email endpoints
    │   └── scheduler.py             # Scheduler endpoints
    └── workers/
        ├── __init__.py
        ├── scheduler.py             # APScheduler setup
        └── tasks.py                 # Background task definitions
```

## Technology Stack

- **Framework**: FastAPI (async web framework)
- **Server**: Uvicorn (ASGI server)
- **Database**: SQLite with SQLAlchemy ORM
- **Task Scheduling**: APScheduler with asyncio
- **Email**: Gmail API (Google Cloud)
- **Messaging**: Telegram Bot API
- **AI/LLM**: OpenAI GPT API
- **Authentication**: OAuth2 (Google), API Keys (OpenAI, Telegram)
- **Configuration**: Pydantic Settings, python-dotenv

## Prerequisites

- Python 3.9+
- Gmail Account with 2-Factor Authentication enabled
- Telegram Bot Token (from @BotFather)
- OpenAI API Key
- Google Cloud Project with Gmail API enabled

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/personal-assistant-bot.git
cd personal-assistant-bot
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop Application)
5. Download credentials as JSON and save as `credentials.json`
6. First run will trigger OAuth2 flow to get access token

### 5. Get Telegram Bot Token

1. Open Telegram and search for @BotFather
2. Create a new bot with `/newbot`
3. Copy the API token provided

### 6. Get Your Telegram User ID

1. Open Telegram and search for @userinfobot
2. Start the bot to see your user ID

### 7. Get OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy it securely

### 8. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_USER_ID=your_user_id
OPENAI_API_KEY=your_openai_key
GMAIL_CREDENTIALS_FILE=credentials.json
```

## Running the Application

### Development Mode
```bash
python main.py
```

The server will start at `http://127.0.0.1:8000`

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### With Hot Reload
```bash
uvicorn main:app --reload
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **API Info**: http://127.0.0.1:8000/api/info
- **API Docs**: http://127.0.0.1:8000/api/docs

## Usage Examples

### Telegram Commands

```
/start - Show welcome message and commands
/emails - Get your latest unread emails
/tasks - Show pending tasks
/summary - Get daily summary
/help - Show available commands
```

### Natural Language Commands via Telegram

```
"Send an email to john@example.com saying hello"
"Read my unread emails"
"Schedule a meeting reminder at 2pm"
"What are my pending tasks?"
```

### API Examples

#### Get Unread Emails
```bash
curl http://localhost:8000/email/unread
```

#### Send Email
```bash
curl -X POST http://localhost:8000/email/send \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "user@example.com",
    "subject": "Hello",
    "body": "This is a test email"
  }'
```

#### Schedule a Task
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

#### Execute a Command
```bash
curl -X POST http://localhost:8000/telegram/command \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Send an email to john@example.com saying hello"
  }'
```

#### List Scheduled Jobs
```bash
curl http://localhost:8000/scheduler/jobs
```

## Configuration

### Environment Variables

Key configuration options in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_TOKEN` | Your Telegram bot token | Required |
| `TELEGRAM_USER_ID` | Your Telegram user ID | Required |
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `GMAIL_CREDENTIALS_FILE` | Gmail OAuth credentials file | credentials.json |
| `SCHEDULER_ENABLED` | Enable background scheduler | True |
| `MORNING_SUMMARY_TIME` | Daily morning summary time (HH:MM) | 08:00 |
| `EVENING_SUMMARY_TIME` | Daily evening summary time (HH:MM) | 20:00 |
| `TIMEZONE` | Scheduler timezone | UTC |
| `DATABASE_URL` | SQLite database path | sqlite:///./bot_database.db |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |

## Database

The bot uses SQLite for persistence with the following tables:

- **tasks**: Scheduled tasks and their status
- **emails**: Email history and metadata
- **messages**: Telegram message history
- **scheduled_jobs**: Recurring job definitions

Database is automatically initialized on first run.

## Logging

Logs are written to both console and file:
- Console: Real-time information
- File: `logs/bot.log` for historical reference

Configure log level in `.env`:
```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## Advanced Configuration

### Custom Cron Schedules

Schedule jobs using cron expressions:
```python
# Every day at 9:00 AM
"0 9 * * *"

# Every Monday at 8:00 AM
"0 8 * * 1"

# Every hour
"0 * * * *"

# Every 30 minutes
"*/30 * * * *"
```

### Email Auto-Reply Rules

Extend the system with custom rules in `app/workers/tasks.py`:

```python
async def auto_reply_emails(db: Session):
    """Auto-reply to emails based on rules"""
    # Implement custom logic for different email types
    # e.g., urgent emails, invoices, calendar invites
```

### Custom Commands

Add new Telegram commands in `app/routers/telegram.py`:

```python
elif command == "custom_command":
    # Your implementation here
    return "Response to custom command"
```

## Troubleshooting

### Gmail Authentication Issues
- Ensure 2-Factor Authentication is enabled
- Check that Gmail API is enabled in Google Cloud Console
- Delete `token.json` to force re-authentication

### Telegram Bot Not Responding
- Verify `TELEGRAM_TOKEN` is correct
- Check bot is started with @BotFather
- Ensure `TELEGRAM_USER_ID` is correct (from @userinfobot)

### Scheduler Not Running
- Ensure `SCHEDULER_ENABLED=True` in .env
- Check logs for any scheduler errors
- Verify APScheduler dependencies are installed

### Email Sending Fails
- Verify Gmail credentials and OAuth token
- Check recipient email format
- Ensure bot has necessary Gmail permissions

## Performance Optimization

- Use connection pooling for database
- Implement caching for frequently accessed data
- Configure email check intervals appropriately
- Monitor task execution times in logs

## Security Considerations

1. **Never commit `.env` file** - Always use `.env.example`
2. **Rotate API keys regularly** - OpenAI, Telegram, Gmail
3. **Use HTTPS in production** - For webhook endpoints
4. **Validate Telegram messages** - Verify webhook signatures
5. **Limit API access** - Use API rate limiting

## Future Enhancements

- [ ] Calendar integration (Google Calendar)
- [ ] Notion integration for task management
- [ ] WhatsApp bot support
- [ ] Database support for PostgreSQL/MySQL
- [ ] Advanced NLP for better intent recognition
- [ ] Custom workflow builder
- [ ] Email template system
- [ ] Multi-language support
- [ ] Machine learning-based email categorization

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review example configurations

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [APScheduler](https://apscheduler.readthedocs.io/) - Task scheduling
- [OpenAI](https://openai.com/) - LLM and AI features
- [Google Cloud](https://cloud.google.com/) - Gmail API
- [Telegram](https://telegram.org/) - Bot API

---

**Built with ❤️ for automation enthusiasts**

Last Updated: December 2024
