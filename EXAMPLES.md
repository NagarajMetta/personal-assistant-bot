# Personal Assistant Bot - Usage Examples

## Complete Examples for All Features

### 1. Gmail Email Operations

#### Reading Unread Emails
```bash
# Via API
curl http://localhost:8000/email/unread?limit=5

# Response
[
  {
    "gmail_id": "abc123",
    "sender": "boss@company.com",
    "subject": "Project Update Needed",
    "body": "Can you provide an update on...",
    "summary": "Boss asking for project status update",
    "priority": "high",
    "is_unread": true,
    "received_at": "2024-01-15T10:30:00"
  }
]
```

#### Via Telegram
```
User: /emails
Bot: 📧 Your latest emails:

From: boss@company.com
Subject: Project Update Needed
```

#### Sending Email
```bash
curl -X POST http://localhost:8000/email/send \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "john@example.com",
    "subject": "Meeting Tomorrow",
    "body": "<h1>Hi John</h1><p>Let'\''s meet tomorrow at 2pm</p>",
    "cc": ["manager@company.com"]
  }'
```

#### Create Draft
```bash
curl -X POST http://localhost:8000/email/draft \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "jane@example.com",
    "subject": "Proposal Review",
    "body": "Here is the proposal..."
  }'
```

### 2. Telegram Bot Commands

#### Start Bot
```
User: /start

Bot: 🤖 Personal Assistant Bot

Available commands:
/emails - Read unread emails
/tasks - Show pending tasks
/summary - Get daily summary
```

#### Read Emails
```
User: /emails

Bot: 📧 Your latest emails:
From: john@example.com
Subject: Meeting Tomorrow
```

### 3. Task Scheduling

#### Schedule Daily Task
```bash
curl -X POST http://localhost:8000/scheduler/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "Morning Email Check",
    "command": "check_emails",
    "schedule_time": "08:00",
    "job_type": "daily"
  }'
```

#### List Scheduled Jobs
```bash
curl http://localhost:8000/scheduler/jobs
```

### 4. Natural Language Commands

#### Via Telegram
```
User: Send an email to john@example.com saying let's meet tomorrow

Bot: ✅ Email sent to john@example.com
```

---

See README.md and QUICKSTART.md for more examples!
