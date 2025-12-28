"""Gmail service for reading and sending emails via Gmail API"""

import base64
import logging
from typing import List, Optional
from email.mime.text import MIMEText
from pathlib import Path
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.oauth2.credentials import Credentials as UserCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.config import get_settings
from app.models.schemas import EmailSchema

logger = logging.getLogger(__name__)


class GmailService:
    """Service for Gmail operations including read, send, and OAuth2 authentication"""

    def __init__(self):
        """Initialize Gmail service"""
        self.settings = get_settings()
        self.service = None
        self._initialize_service()

    def _initialize_service(self):
        """Initialize Gmail API service with OAuth2 credentials"""
        try:
            creds = self._get_credentials()
            self.service = build("gmail", "v1", credentials=creds)
            logger.info("Gmail service initialized successfully")
        except FileNotFoundError as e:
            logger.warning(f"Gmail credentials not found: {e}. Gmail service disabled.")
            self.service = None
        except Exception as e:
            logger.error(f"Failed to initialize Gmail service: {e}")
            self.service = None

    def _get_credentials(self) -> UserCredentials:
        """
        Get or refresh Gmail API credentials using OAuth2

        Returns:
            Credentials: Valid Gmail API credentials
        """
        token_path = Path(self.settings.GMAIL_TOKEN_FILE)
        credentials_path = Path(self.settings.GMAIL_CREDENTIALS_FILE)

        creds = None

        # Load existing token if available
        if token_path.exists():
            try:
                creds = UserCredentials.from_authorized_user_file(
                    token_path, self.settings.GMAIL_SCOPES
                )
                logger.debug("Loaded existing Gmail credentials from token")
            except Exception as e:
                logger.warning(f"Failed to load existing token: {e}")

        # If no valid credentials, perform OAuth2 flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logger.info("Refreshed Gmail credentials")
                except RefreshError as e:
                    logger.warning(f"Failed to refresh credentials: {e}")
                    creds = None

            if not creds:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, self.settings.GMAIL_SCOPES
                )
                creds = flow.run_local_server(port=0)
                logger.info("Obtained new Gmail credentials via OAuth2")

            # Save credentials for future use
            with open(token_path, "w") as token:
                token.write(creds.to_json())
                logger.debug("Saved Gmail credentials to token file")

        return creds

    def get_unread_emails(
        self, max_results: int = 10, summary_ai=None
    ) -> List[EmailSchema]:
        """
        Fetch unread emails from Gmail

        Args:
            max_results: Maximum number of emails to fetch
            summary_ai: Optional AI service for summarizing emails

        Returns:
            List of email schemas
        """
        try:
            results = self.service.users().messages().list(
                userId="me", q="is:unread", maxResults=max_results
            ).execute()

            messages = results.get("messages", [])
            emails = []

            for message in messages:
                email_data = self._parse_message(message["id"])
                if email_data:
                    # Optionally summarize with AI
                    if summary_ai:
                        email_data["summary"] = summary_ai.summarize_text(
                            email_data["body"]
                        )
                    emails.append(email_data)

            logger.info(f"Retrieved {len(emails)} unread emails")
            return emails

        except HttpError as error:
            logger.error(f"Failed to fetch emails: {error}")
            return []

    def _parse_message(self, message_id: str) -> Optional[dict]:
        """
        Parse a Gmail message into email schema

        Args:
            message_id: Gmail message ID

        Returns:
            Email data dictionary or None if parsing fails
        """
        try:
            message = self.service.users().messages().get(
                userId="me", id=message_id, format="full"
            ).execute()

            headers = message["payload"]["headers"]
            subject = next(
                (h["value"] for h in headers if h["name"] == "Subject"), "No Subject"
            )
            sender = next(
                (h["value"] for h in headers if h["name"] == "From"), "Unknown"
            )
            date_str = next(
                (h["value"] for h in headers if h["name"] == "Date"), None
            )

            # Extract email body
            body = self._get_message_body(message)

            # Parse date
            received_at = self._parse_email_date(date_str) if date_str else datetime.utcnow()

            return EmailSchema(
                gmail_id=message_id,
                sender=sender,
                subject=subject,
                body=body,
                received_at=received_at,
            ).model_dump()

        except Exception as e:
            logger.error(f"Failed to parse message {message_id}: {e}")
            return None

    def _get_message_body(self, message: dict) -> str:
        """
        Extract message body from Gmail message payload

        Args:
            message: Gmail message object

        Returns:
            Message body text
        """
        try:
            if "parts" in message["payload"]:
                # Multi-part message
                for part in message["payload"]["parts"]:
                    if part["mimeType"] == "text/plain":
                        data = part["body"].get("data", "")
                        return base64.urlsafe_b64decode(data).decode("utf-8")
            else:
                # Simple message
                data = message["payload"]["body"].get("data", "")
                return base64.urlsafe_b64decode(data).decode("utf-8")
        except Exception as e:
            logger.warning(f"Failed to extract message body: {e}")
            return "[Unable to extract message body]"

    def _parse_email_date(self, date_str: str) -> datetime:
        """
        Parse email date string from Gmail headers

        Args:
            date_str: Date string from email header

        Returns:
            Parsed datetime object
        """
        try:
            from email.utils import parsedate_to_datetime

            return parsedate_to_datetime(date_str)
        except Exception as e:
            logger.warning(f"Failed to parse email date '{date_str}': {e}")
            return datetime.utcnow()

    def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ) -> bool:
        """
        Send an email via Gmail

        Args:
            recipient: Email recipient address
            subject: Email subject
            body: Email body (HTML or plain text)
            cc: List of CC recipients
            bcc: List of BCC recipients

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            message = MIMEText(body, "html" if "<html>" in body.lower() else "plain")
            message["To"] = recipient
            message["Subject"] = subject

            if cc:
                message["Cc"] = ", ".join(cc)
            if bcc:
                message["Bcc"] = ", ".join(bcc)

            raw_message = base64.urlsafe_b64encode(
                message.as_bytes()
            ).decode("utf-8")

            send_message = {"raw": raw_message}

            self.service.users().messages().send(
                userId="me", body=send_message
            ).execute()

            logger.info(f"Email sent successfully to {recipient}")
            return True

        except HttpError as error:
            logger.error(f"Failed to send email: {error}")
            return False

    def mark_as_read(self, message_id: str) -> bool:
        """
        Mark a message as read

        Args:
            message_id: Gmail message ID

        Returns:
            True if successful, False otherwise
        """
        try:
            self.service.users().messages().modify(
                userId="me",
                id=message_id,
                body={"removeLabelIds": ["UNREAD"]},
            ).execute()
            return True
        except HttpError as error:
            logger.error(f"Failed to mark message as read: {error}")
            return False

    def create_draft(
        self, recipient: str, subject: str, body: str
    ) -> Optional[str]:
        """
        Create a draft email

        Args:
            recipient: Recipient email address
            subject: Email subject
            body: Email body

        Returns:
            Draft ID if successful, None otherwise
        """
        try:
            message = MIMEText(body)
            message["To"] = recipient
            message["Subject"] = subject

            raw_message = base64.urlsafe_b64encode(
                message.as_bytes()
            ).decode("utf-8")

            draft_body = {"message": {"raw": raw_message}}

            draft = self.service.users().drafts().create(
                userId="me", body=draft_body
            ).execute()

            logger.info(f"Draft created with ID: {draft['id']}")
            return draft["id"]

        except HttpError as error:
            logger.error(f"Failed to create draft: {error}")
            return None

    def get_email_by_label(self, label: str, max_results: int = 5) -> List[dict]:
        """
        Get emails by Gmail label

        Args:
            label: Gmail label (e.g., 'INBOX', 'STARRED')
            max_results: Maximum number of emails to fetch

        Returns:
            List of email data
        """
        try:
            results = self.service.users().messages().list(
                userId="me", q=f"label:{label}", maxResults=max_results
            ).execute()

            messages = results.get("messages", [])
            emails = []

            for message in messages:
                email_data = self._parse_message(message["id"])
                if email_data:
                    emails.append(email_data)

            logger.info(f"Retrieved {len(emails)} emails with label '{label}'")
            return emails

        except HttpError as error:
            logger.error(f"Failed to fetch emails by label: {error}")
            return []
