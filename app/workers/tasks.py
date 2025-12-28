"""Background worker tasks and job handlers"""

import logging
from typing import List
from datetime import datetime
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.database import Task, TaskStatus, Email, ScheduledJob
from app.services.gmail_service import GmailService
from app.services.telegram_service import TelegramService
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)

settings = get_settings()


async def check_emails(ai_service: AIService = None) -> dict:
    """
    Background task to check and process unread emails

    Args:
        ai_service: Optional AI service for summarization

    Returns:
        Dictionary with task results
    """
    if not settings.GMAIL_ENABLED:
        logger.info("Gmail operations disabled - skipping email check")
        return {"status": "skipped", "reason": "Gmail disabled"}
    
    try:
        gmail = GmailService()
        telegram = TelegramService()

        emails = gmail.get_unread_emails(max_results=5, summary_ai=ai_service)

        if not emails:
            logger.info("No unread emails")
            return {"status": "success", "count": 0}

        # Send summary to Telegram
        message = f"📧 <b>You have {len(emails)} unread emails:</b>\n\n"

        for email in emails[:3]:  # Show top 3
            summary = email.get("summary", email["body"][:100])
            message += f"<b>From:</b> {email['sender']}\n"
            message += f"<b>Subject:</b> {email['subject']}\n"
            message += f"<b>Summary:</b> {summary}\n\n"

        await telegram.send_message(message)

        logger.info(f"Processed {len(emails)} emails")
        return {"status": "success", "count": len(emails)}

    except Exception as e:
        logger.error(f"Error checking emails: {e}")
        return {"status": "error", "error": str(e)}


async def send_daily_summary(ai_service: AIService = None) -> dict:
    """
    Background task to send daily summary

    Args:
        ai_service: AI service for generating summary

    Returns:
        Dictionary with task results
    """
    if not settings.GMAIL_ENABLED:
        logger.info("Gmail operations disabled - sending Telegram-only summary")
    
    try:
        telegram = TelegramService()

        # Get email count only if Gmail is enabled
        if settings.GMAIL_ENABLED:
            gmail = GmailService()
            emails = gmail.get_unread_emails(max_results=100)
            email_count = len(emails)
        else:
            email_count = 0

        # Generate summary
        pending_tasks = ["Task 1", "Task 2"]  # Placeholder
        completed_tasks = ["Completed 1"]  # Placeholder

        summary = "📋 <b>Daily Summary</b>\n\n"
        if settings.GMAIL_ENABLED:
            summary += f"📧 Unread emails: {email_count}\n"
        summary += f"⏳ Pending tasks: {len(pending_tasks)}\n"
        summary += f"✅ Completed today: {len(completed_tasks)}\n\n"

        if ai_service:
            ai_summary = ai_service.generate_daily_summary(
                email_count, pending_tasks, completed_tasks
            )
            summary += f"<i>{ai_summary}</i>"

        await telegram.send_message(summary)

        logger.info("Daily summary sent")
        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error sending daily summary: {e}")
        return {"status": "error", "error": str(e)}


async def process_scheduled_tasks(db: Session) -> dict:
    """
    Process pending scheduled tasks

    Args:
        db: Database session

    Returns:
        Dictionary with results
    """
    try:
        pending_tasks = db.query(Task).filter(
            Task.status == TaskStatus.PENDING
        ).all()

        results = {"processed": 0, "failed": 0}

        for task in pending_tasks:
            try:
                logger.info(f"Processing task: {task.name}")
                # Task processing logic here
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.utcnow()
                results["processed"] += 1
            except Exception as e:
                logger.error(f"Failed to process task {task.name}: {e}")
                task.status = TaskStatus.FAILED
                task.error_message = str(e)
                results["failed"] += 1

        db.commit()
        return {"status": "success", **results}

    except Exception as e:
        logger.error(f"Error processing scheduled tasks: {e}")
        return {"status": "error", "error": str(e)}


async def cleanup_old_data(db: Session, days: int = 30) -> dict:
    """
    Clean up old data from database

    Args:
        db: Database session
        days: Delete data older than this many days

    Returns:
        Dictionary with cleanup results
    """
    try:
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Clean up old completed tasks
        old_tasks = db.query(Task).filter(
            Task.completed_at < cutoff_date,
            Task.status == TaskStatus.COMPLETED,
        ).delete()

        # Clean up old messages
        from app.models.database import Message

        old_messages = db.query(Message).filter(
            Message.created_at < cutoff_date
        ).delete()

        db.commit()

        logger.info(f"Cleaned up {old_tasks} old tasks and {old_messages} old messages")
        return {
            "status": "success",
            "deleted_tasks": old_tasks,
            "deleted_messages": old_messages,
        }

    except Exception as e:
        logger.error(f"Error cleaning up old data: {e}")
        return {"status": "error", "error": str(e)}


async def sync_gmail_to_db(db: Session) -> dict:
    """
    Sync Gmail unread emails to database

    Args:
        db: Database session

    Returns:
        Dictionary with sync results
    """
    try:
        gmail = GmailService()
        ai = AIService()

        emails = gmail.get_unread_emails(max_results=10, summary_ai=ai)

        saved_count = 0
        for email_data in emails:
            # Check if email already exists
            existing = db.query(Email).filter(
                Email.gmail_id == email_data["gmail_id"]
            ).first()

            if not existing:
                email = Email(
                    gmail_id=email_data["gmail_id"],
                    sender=email_data["sender"],
                    subject=email_data["subject"],
                    body=email_data["body"],
                    summary=email_data.get("summary"),
                    received_at=email_data["received_at"],
                )
                db.add(email)
                saved_count += 1

        db.commit()
        logger.info(f"Synced {saved_count} new emails to database")
        return {"status": "success", "saved": saved_count}

    except Exception as e:
        logger.error(f"Error syncing emails: {e}")
        return {"status": "error", "error": str(e)}
