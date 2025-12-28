"""Email management router"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.schemas import EmailSchema
from app.models.database import get_db, Email
from app.services.gmail_service import GmailService
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/email", tags=["email"])

settings = get_settings()
gmail_service = GmailService()
ai_service = AIService()


@router.get("/unread", response_model=List[EmailSchema])
async def get_unread_emails(
    limit: int = 10, db: Session = Depends(get_db)
) -> List[EmailSchema]:
    """
    Get unread emails from Gmail

    Args:
        limit: Maximum number of emails to fetch
        db: Database session

    Returns:
        List of unread emails
    """
    if not settings.GMAIL_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="Gmail operations are currently disabled. Enable GMAIL_ENABLED in .env"
        )
    
    try:
        emails = gmail_service.get_unread_emails(
            max_results=limit, summary_ai=ai_service
        )

        # Save to database
        for email_data in emails:
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

        db.commit()

        return emails

    except Exception as e:
        logger.error(f"Error fetching unread emails: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/inbox", response_model=List[EmailSchema])
async def get_inbox_emails(limit: int = 20) -> List[EmailSchema]:
    """
    Get emails from inbox

    Args:
        limit: Maximum number of emails

    Returns:
        List of inbox emails
    """
    try:
        return gmail_service.get_email_by_label("INBOX", max_results=limit)
    except Exception as e:
        logger.error(f"Error fetching inbox: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send")
async def send_email(
    recipient: str,
    subject: str,
    body: str,
    cc: list = None,
    bcc: list = None,
) -> dict:
    """
    Send an email via Gmail

    Args:
        recipient: Email recipient
        subject: Email subject
        body: Email body (HTML or plain text)
        cc: CC recipients
        bcc: BCC recipients

    Returns:
        Send status
    """
    try:
        success = gmail_service.send_email(recipient, subject, body, cc, bcc)

        return {
            "status": "sent" if success else "failed",
            "recipient": recipient,
            "subject": subject,
        }

    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/draft")
async def create_draft(recipient: str, subject: str, body: str) -> dict:
    """
    Create an email draft

    Args:
        recipient: Email recipient
        subject: Email subject
        body: Email body

    Returns:
        Draft creation status
    """
    try:
        draft_id = gmail_service.create_draft(recipient, subject, body)

        if draft_id:
            return {"status": "created", "draft_id": draft_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to create draft")

    except Exception as e:
        logger.error(f"Error creating draft: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary/{email_id}")
async def get_email_summary(email_id: int, db: Session = Depends(get_db)) -> dict:
    """
    Get or generate summary for an email

    Args:
        email_id: Email ID in database
        db: Database session

    Returns:
        Email summary
    """
    try:
        email = db.query(Email).filter(Email.id == email_id).first()

        if not email:
            raise HTTPException(status_code=404, detail="Email not found")

        if not email.summary:
            email.summary = ai_service.summarize_email(email.subject, email.body)
            db.commit()

        return {
            "id": email.id,
            "subject": email.subject,
            "summary": email.summary,
        }

    except Exception as e:
        logger.error(f"Error getting email summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mark-read/{message_id}")
async def mark_email_read(message_id: str) -> dict:
    """
    Mark an email as read

    Args:
        message_id: Gmail message ID

    Returns:
        Operation result
    """
    try:
        success = gmail_service.mark_as_read(message_id)
        return {
            "status": "marked" if success else "failed",
            "message_id": message_id,
        }
    except Exception as e:
        logger.error(f"Error marking email as read: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/labels")
async def get_email_labels() -> dict:
    """
    Get available Gmail labels

    Returns:
        Dictionary of available labels
    """
    return {
        "labels": ["INBOX", "STARRED", "SENT", "DRAFT", "SPAM", "TRASH", "ALL_MAIL"]
    }
