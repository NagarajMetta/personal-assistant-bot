"""Telegram bot webhook and message handler router"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.schemas import TelegramUpdate, CommandRequest
from app.models.database import get_db, Message
from app.services.telegram_service import TelegramService
from app.services.ai_service import AIService
from app.services.gmail_service import GmailService
from app.services.realtime_service import RealtimeService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/telegram", tags=["telegram"])

settings = get_settings()
telegram_service = TelegramService()
ai_service = AIService()
realtime_service = RealtimeService()

# Initialize Gmail service with explicit logging
gmail_service = None
if settings.GMAIL_ENABLED:
    try:
        gmail_service = GmailService()
        if gmail_service.service:
            logger.info("Gmail service initialized successfully in telegram router")
        else:
            logger.warning("Gmail service created but service is None - check token.json")
    except Exception as e:
        logger.error(f"Failed to initialize Gmail service: {e}")
        gmail_service = None
else:
    logger.info("Gmail is disabled in settings")


@router.post("/webhook")
async def telegram_webhook(update: dict, db: Session = Depends(get_db)):
    """
    Telegram webhook endpoint for receiving messages

    Args:
        update: Telegram update object
        db: Database session
    """
    try:
        logger.info(f"Received Telegram update: {update}")

        # Parse the message
        message_data = telegram_service.parse_message(update)
        
        logger.info(f"Parsed message data: {message_data}")

        # Save message to database
        msg = Message(
            telegram_message_id=str(message_data["message_id"]),
            user_id=message_data["user_id"],
            text=message_data["text"],
            command=message_data["command"],
            is_command=message_data["is_command"],
        )
        db.add(msg)
        db.commit()

        # Process based on message type
        if message_data["is_command"]:
            logger.info(f"Processing as command: {message_data['command']}")
            response = await _handle_command(
                message_data["command"],
                message_data["text"],
                message_data["user_id"],
                db,
            )
        else:
            response = await _handle_natural_language(
                message_data["text"],
                message_data["user_id"],
                db,
            )

        # Send response
        if response:
            await telegram_service.send_message(response, message_data["user_id"])

        # Update message with response
        msg.response = response
        db.commit()

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error processing telegram webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _handle_command(
    command: str, text: str, user_id: int, db: Session
) -> str:
    """Handle slash commands"""
    
    if command == "start":
        return """🤖 <b>Personal Assistant Bot</b>

I can help you with:
• 📧 Reading and sending emails
• 📋 Managing tasks and reminders
• 🕐 Scheduling messages
• 📊 Daily summaries
• 📈 Real-time stock prices
• 🪙 Cryptocurrency prices
• 🌤️ Weather updates
• 🌍 World clock

Type a command or describe what you need!

<b>Examples:</b>
• "What's the stock price of AAPL?"
• "Bitcoin price"
• "Time in Tokyo"
• "Weather in London"
• "What is machine learning?"

Available commands:
/emails - Read unread emails
/tasks - Show pending tasks
/schedule - Schedule a task
/summary - Get daily summary
/help - Show this message"""

    elif command == "emails":
        if not gmail_service or not gmail_service.service:
            return "📧 Email service not configured. Please set up Gmail OAuth first."
        
        emails = gmail_service.get_unread_emails(max_results=5)
        
        if not emails:
            return "📭 No unread emails found!"
        
        response = f"📧 <b>Unread Emails ({len(emails)})</b>\n\n"
        for i, email in enumerate(emails, 1):
            sender = email.get('sender', 'Unknown')[:30]
            subject = email.get('subject', 'No Subject')[:40]
            response += f"{i}. <b>From:</b> {sender}\n   <b>Subject:</b> {subject}\n\n"
        
        return response

    elif command == "tasks":
        from app.models.database import Task, TaskStatus

        tasks = db.query(Task).filter(
            Task.status == TaskStatus.PENDING
        ).limit(5).all()

        if not tasks:
            return "✅ No pending tasks"

        response = "📋 <b>Pending tasks:</b>\n\n"
        for task in tasks:
            response += f"• {task.name}\n"
        return response

    elif command == "summary":
        from app.workers.tasks import send_daily_summary

        result = await send_daily_summary(ai_service)
        return "📊 Daily summary sent!"

    elif command == "help":
        return "Use /start to see available commands"

    else:
        return f"❓ Unknown command: /{command}\nType /help for available commands"


async def _handle_natural_language(text: str, user_id: int, db: Session) -> str:
    """Handle natural language messages"""
    try:
        logger.info(f"Handling natural language message: '{text}' from user {user_id}")
        
        # Parse the command using AI
        parsed = ai_service.parse_command(text)

        action = parsed.get("action", "unknown")
        parameters = parsed.get("parameters", {})
        
        logger.info(f"Parsed action: {action}, parameters: {parameters}")

        if action == "read_emails":
            if not gmail_service or not gmail_service.service:
                return "📧 Email service not configured. Please set up Gmail OAuth first."
            
            emails = gmail_service.get_unread_emails(max_results=5)
            
            if not emails:
                return "📭 No unread emails found!"
            
            response = f"📧 <b>Unread Emails ({len(emails)})</b>\n\n"
            for i, email in enumerate(emails, 1):
                sender = email.get('sender', 'Unknown')[:30]
                subject = email.get('subject', 'No Subject')[:40]
                response += f"{i}. <b>From:</b> {sender}\n   <b>Subject:</b> {subject}\n\n"
            
            return response

        elif action == "send_email":
            logger.info(f"Send email action triggered. gmail_service={gmail_service is not None}, service={gmail_service.service if gmail_service else None}")
            
            if not gmail_service or not gmail_service.service:
                logger.error("Gmail service not available for sending email")
                return "📧 Email service not configured. Please set up Gmail OAuth first."
            
            recipient = parameters.get("recipient", "")
            
            logger.info(f"Attempting to send email to: {recipient}")
            
            if not recipient or "@" not in recipient:
                return "❌ Please provide a valid email address. Example: 'Send email to name@example.com saying Hello'"
            
            # Extract the actual message from the command
            subject = "Message from Personal Assistant Bot"
            email_body = None
            
            # Try to extract actual message content using multiple patterns
            text_lower = text.lower()
            
            # Pattern 1: "saying ..." or "with message ..." etc.
            for phrase in ["saying ", "with message ", "message: ", "body: ", "content: ", "that ", "with body "]:
                if phrase in text_lower:
                    idx = text_lower.find(phrase) + len(phrase)
                    email_body = text[idx:].strip()
                    break
            
            # Pattern 2: Extract text after the email address
            if not email_body:
                import re
                # Find text after email address
                match = re.search(r'[\w\.-]+@[\w\.-]+\s+(.+)', text, re.IGNORECASE)
                if match:
                    remaining = match.group(1).strip()
                    # Remove common connector words at the start
                    for prefix in ["saying", "with", "message", "body", "content", "that"]:
                        if remaining.lower().startswith(prefix):
                            remaining = remaining[len(prefix):].strip()
                            break
                    if remaining:
                        email_body = remaining
            
            # Pattern 3: If user just says "send email to X" without content, ask for content
            if not email_body or len(email_body) < 3:
                return f"📝 What would you like to say in the email to {recipient}?\n\nExample: Send email to {recipient} saying Hello, how are you?"
            
            logger.info(f"Email body extracted: {email_body[:50]}...")
            
            success = gmail_service.send_email(
                recipient=recipient,
                subject=subject,
                body=email_body
            )
            
            if success:
                return f"✅ Email sent successfully to {recipient}!\n\n📧 <b>Message:</b> {email_body[:100]}{'...' if len(email_body) > 100 else ''}"
            else:
                return f"❌ Failed to send email to {recipient}. Please try again."

        elif action == "send_message":
            # For scheduling messages
            return "💬 Message scheduling coming soon!"

        elif action == "ask_question":
            # General Q&A using OpenAI
            question = parameters.get("question", text)
            logger.info(f"Processing Q&A request: {question}")
            answer = ai_service.answer_question(question)
            return f"🤖 {answer}"

        elif action == "get_stock_price":
            # Real-time stock price
            symbol = parameters.get("symbol", "AAPL")
            logger.info(f"Getting stock price for: {symbol}")
            result = await realtime_service.get_stock_price(symbol)
            
            if result.get("success"):
                change_emoji = "📈" if result["change"] >= 0 else "📉"
                change_sign = "+" if result["change"] >= 0 else ""
                return (
                    f"📊 <b>{result['name']}</b> ({result['symbol']})\n\n"
                    f"💰 Price: <b>${result['price']}</b> {result['currency']}\n"
                    f"{change_emoji} Change: {change_sign}${result['change']} ({change_sign}{result['change_percent']}%)"
                )
            else:
                return f"❌ {result.get('error', 'Failed to get stock price')}"

        elif action == "get_crypto_price":
            # Real-time cryptocurrency price
            symbol = parameters.get("symbol", "BTC")
            logger.info(f"Getting crypto price for: {symbol}")
            result = await realtime_service.get_crypto_price(symbol)
            
            if result.get("success"):
                change_emoji = "📈" if result["change_24h"] >= 0 else "📉"
                change_sign = "+" if result["change_24h"] >= 0 else ""
                return (
                    f"🪙 <b>{result['name']}</b> ({result['symbol']})\n\n"
                    f"💰 Price: <b>${result['price']:,.2f}</b> {result['currency']}\n"
                    f"{change_emoji} 24h Change: {change_sign}{result['change_24h']:.2f}%"
                )
            else:
                return f"❌ {result.get('error', 'Failed to get crypto price')}"

        elif action == "get_time":
            # Current time in a city
            city = parameters.get("city", "New York")
            logger.info(f"Getting time for: {city}")
            result = realtime_service.get_time_in_city(city)
            
            if result.get("success"):
                return (
                    f"🕐 <b>Time in {result['city']}</b>\n\n"
                    f"⏰ <b>{result['time']}</b> ({result['time_24']})\n"
                    f"📅 {result['date']}\n"
                    f"🌍 Timezone: {result['timezone']}"
                )
            else:
                return f"❌ {result.get('error', 'Failed to get time')}"

        elif action == "get_weather":
            # Real-time weather
            city = parameters.get("city", "New York")
            logger.info(f"Getting weather for: {city}")
            result = await realtime_service.get_weather(city)
            
            if result.get("success"):
                return (
                    f"🌤️ <b>Weather in {result['city']}, {result['country']}</b>\n\n"
                    f"🌡️ Temperature: <b>{result['temperature_c']}°C</b> ({result['temperature_f']}°F)\n"
                    f"🤗 Feels like: {result['feels_like_c']}°C\n"
                    f"☁️ Conditions: {result['description']}\n"
                    f"💧 Humidity: {result['humidity']}%\n"
                    f"💨 Wind: {result['wind_kmph']} km/h"
                )
            else:
                return f"❌ {result.get('error', 'Failed to get weather')}"

        elif action == "unknown":
            # For unknown actions, try answering as a general question
            logger.info(f"Unknown action - trying Q&A fallback for: {text}")
            answer = ai_service.answer_question(text)
            return f"🤖 {answer}"

        elif action == "schedule_task":
            task_name = parameters.get("task_name", "Scheduled Task")
            scheduled_time = parameters.get("time")

            return f"🕐 Task '{task_name}' scheduled for {scheduled_time}"
        
        else:
            # DEFAULT: Answer any other message as a question using AI
            logger.info(f"Default action - answering as Q&A: {text}")
            answer = ai_service.answer_question(text)
            return f"🤖 {answer}"

    except Exception as e:
        logger.error(f"Error processing natural language: {e}")
        # Even on error, try to answer the question
        try:
            answer = ai_service.answer_question(text)
            return f"🤖 {answer}"
        except:
            return "❌ Sorry, I had trouble understanding that. Please try again or use /help."


@router.post("/command")
async def handle_command(
    request: CommandRequest, db: Session = Depends(get_db)
) -> dict:
    """
    Manually trigger a command via API

    Args:
        request: Command request
        db: Database session

    Returns:
        Command execution result
    """
    try:
        parsed = ai_service.parse_command(request.text)
        action = parsed.get("action", "unknown")

        logger.info(f"Executing command: {action}")

        result = {
            "action": action,
            "parameters": parsed.get("parameters", {}),
            "confidence": parsed.get("confidence", 0),
        }

        return result

    except Exception as e:
        logger.error(f"Error executing command: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_bot_status() -> dict:
    """
    Get Telegram bot status

    Returns:
        Bot status information
    """
    try:
        bot_info = await telegram_service.get_me()
        return {
            "status": "connected",
            "username": bot_info.get("username") if bot_info else None,
            "first_name": bot_info.get("first_name") if bot_info else None,
        }
    except Exception as e:
        logger.error(f"Error getting bot status: {e}")
        return {"status": "error", "error": str(e)}


@router.post("/send")
async def send_telegram_message(text: str, chat_id: int = None) -> dict:
    """
    Send a Telegram message manually

    Args:
        text: Message text
        chat_id: Optional chat ID (defaults to configured user)

    Returns:
        Execution result
    """
    try:
        success = await telegram_service.send_message(text, chat_id)
        return {"status": "sent" if success else "failed"}
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))
