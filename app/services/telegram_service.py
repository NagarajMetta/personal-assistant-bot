"""Telegram bot service for message handling and command processing"""

import logging
import hmac
import hashlib
from typing import Optional, Dict, Any
import aiohttp
import asyncio

from app.config import get_settings

logger = logging.getLogger(__name__)


class TelegramService:
    """Service for handling Telegram bot operations"""

    def __init__(self):
        """Initialize Telegram service"""
        self.settings = get_settings()
        self.api_url = f"https://api.telegram.org/bot{self.settings.TELEGRAM_BOT_TOKEN}"
        self.user_id = self.settings.TELEGRAM_USER_ID

    def verify_webhook_signature(
        self, body: str, signature: str
    ) -> bool:
        """
        Verify Telegram webhook signature

        Args:
            body: Request body
            signature: X-Telegram-Bot-Api-Secret-Token header

        Returns:
            True if signature is valid
        """
        expected_signature = signature
        if expected_signature == self.settings.TELEGRAM_WEBHOOK_SECRET:
            return True
        logger.warning("Invalid webhook signature")
        return False

    async def send_message(
        self,
        text: str,
        chat_id: Optional[int] = None,
        parse_mode: str = "HTML",
    ) -> bool:
        """
        Send a message via Telegram

        Args:
            text: Message text
            chat_id: Telegram chat ID (defaults to user ID)
            parse_mode: Message parse mode (HTML, Markdown, etc.)

        Returns:
            True if sent successfully
        """
        if not chat_id:
            chat_id = self.user_id

        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/sendMessage", json=payload
                ) as response:
                    if response.status == 200:
                        logger.info(f"Message sent to chat {chat_id}")
                        return True
                    else:
                        logger.error(f"Failed to send message: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False

    async def send_document(
        self,
        file_path: str,
        chat_id: Optional[int] = None,
        caption: Optional[str] = None,
    ) -> bool:
        """
        Send a document via Telegram

        Args:
            file_path: Path to file to send
            chat_id: Telegram chat ID
            caption: Optional document caption

        Returns:
            True if sent successfully
        """
        if not chat_id:
            chat_id = self.user_id

        try:
            with open(file_path, "rb") as file:
                files = {"document": file}
                data = {"chat_id": chat_id}
                if caption:
                    data["caption"] = caption

                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.api_url}/sendDocument",
                        data=data,
                        files=files,
                    ) as response:
                        if response.status == 200:
                            logger.info(f"Document sent to chat {chat_id}")
                            return True
                        else:
                            logger.error(f"Failed to send document: {response.status}")
                            return False
        except Exception as e:
            logger.error(f"Error sending document: {e}")
            return False

    async def set_webhook(self, webhook_url: str) -> bool:
        """
        Set Telegram webhook URL

        Args:
            webhook_url: Full webhook URL

        Returns:
            True if successful
        """
        payload = {"url": webhook_url}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/setWebhook", json=payload
                ) as response:
                    if response.status == 200:
                        logger.info(f"Webhook set to {webhook_url}")
                        return True
                    else:
                        logger.error(f"Failed to set webhook: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Error setting webhook: {e}")
            return False

    async def get_me(self) -> Optional[Dict[str, Any]]:
        """
        Get bot information

        Returns:
            Bot information or None if failed
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/getMe") as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Bot info retrieved: {data['result']['username']}")
                        return data.get("result")
                    return None
        except Exception as e:
            logger.error(f"Error getting bot info: {e}")
            return None

    def parse_message(self, update: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse Telegram update message

        Args:
            update: Telegram update object

        Returns:
            Parsed message data
        """
        message = update.get("message", {})
        return {
            "message_id": message.get("message_id"),
            "chat_id": message.get("chat", {}).get("id"),
            "user_id": message.get("from", {}).get("id"),
            "text": message.get("text", ""),
            "command": self._extract_command(message.get("text", "")),
            "timestamp": message.get("date"),
            "is_command": message.get("text", "").startswith("/"),
        }

    def _extract_command(self, text: str) -> Optional[str]:
        """
        Extract command from message text

        Args:
            text: Message text

        Returns:
            Command name or None
        """
        if text.startswith("/"):
            parts = text.split()
            command = parts[0].lstrip("/")
            return command
        return None

    def format_email_summary(
        self, sender: str, subject: str, summary: str, priority: str = "medium"
    ) -> str:
        """
        Format email data as readable Telegram message

        Args:
            sender: Email sender
            subject: Email subject
            summary: Email summary
            priority: Email priority

        Returns:
            Formatted message
        """
        priority_emoji = {
            "low": "📝",
            "medium": "📧",
            "high": "⚠️",
            "urgent": "🚨",
        }

        emoji = priority_emoji.get(priority, "📧")

        return f"""
{emoji} <b>New Email</b>

<b>From:</b> {sender}
<b>Subject:</b> {subject}
<b>Priority:</b> {priority}

<b>Summary:</b>
{summary}
"""

    def format_task_summary(self, task_name: str, status: str, details: str = "") -> str:
        """
        Format task data as readable Telegram message

        Args:
            task_name: Task name
            status: Task status
            details: Additional details

        Returns:
            Formatted message
        """
        status_emoji = {
            "pending": "⏳",
            "running": "⚙️",
            "completed": "✅",
            "failed": "❌",
        }

        emoji = status_emoji.get(status, "📋")

        message = f"{emoji} <b>{task_name}</b>\n"
        message += f"Status: {status}\n"
        if details:
            message += f"\n{details}"

        return message

    async def edit_message(
        self,
        chat_id: int,
        message_id: int,
        text: str,
        parse_mode: str = "HTML",
    ) -> bool:
        """
        Edit an existing Telegram message

        Args:
            chat_id: Chat ID
            message_id: Message ID to edit
            text: New message text
            parse_mode: Parse mode

        Returns:
            True if successful
        """
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": parse_mode,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/editMessageText", json=payload
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Error editing message: {e}")
            return False

    async def delete_message(self, chat_id: int, message_id: int) -> bool:
        """
        Delete a Telegram message

        Args:
            chat_id: Chat ID
            message_id: Message ID

        Returns:
            True if successful
        """
        payload = {"chat_id": chat_id, "message_id": message_id}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/deleteMessage", json=payload
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Error deleting message: {e}")
            return False
