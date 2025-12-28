"""AI service for intent parsing, command generation, and email summarization"""

import logging
from typing import Optional, Dict, Any
from openai import OpenAI

from app.config import get_settings

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered features using OpenAI API"""

    def __init__(self):
        """Initialize AI service"""
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.OPENAI_API_KEY)
        self.model = self.settings.OPENAI_MODEL
        self.temperature = self.settings.OPENAI_TEMPERATURE
        self.max_tokens = self.settings.OPENAI_MAX_TOKENS

    def parse_command(self, text: str) -> Dict[str, Any]:
        """
        Parse natural language command using AI

        Args:
            text: Natural language command text

        Returns:
            Dictionary with parsed command details
        """
        try:
            import json
            
            logger.info(f"Parsing command: '{text}'")
            
            text_lower = text.lower().strip()
            logger.debug(f"Lowercase text: '{text_lower}'")
            
            # === PATTERN 1: Email related ===
            email_keywords = ["email", "mail", "read", "unread", "inbox", "gmail", "messages"]
            if any(word in text_lower for word in email_keywords):
                logger.info("Pattern match: Email keywords detected")
                
                # Check if it's send_email
                send_keywords = ["send", "write", "compose", "to", "reply"]
                if any(word in text_lower for word in send_keywords):
                    logger.info("Sub-pattern: Send email detected")
                    # Try to find email address
                    recipient = ""
                    for word in text.split():
                        if "@" in word:
                            recipient = word.strip()
                            break
                    
                    return {
                        "action": "send_email",
                        "parameters": {
                            "recipient": recipient,
                            "body": text
                        },
                        "confidence": 90
                    }
                else:
                    # Read emails
                    logger.info("Sub-pattern: Read email detected")
                    return {
                        "action": "read_emails",
                        "parameters": {},
                        "confidence": 90
                    }
            
            # === PATTERN 2: Task/Schedule related ===
            task_keywords = ["task", "todo", "reminder", "schedule", "remind", "alarm", "meeting", "appointment"]
            if any(word in text_lower for word in task_keywords):
                logger.info("Pattern match: Task/schedule keywords detected")
                return {
                    "action": "schedule_task",
                    "parameters": {"task_name": text},
                    "confidence": 85
                }
            
            # === PATTERN 3: Summary related ===
            summary_keywords = ["summary", "daily", "overview", "report", "briefing", "news"]
            if any(word in text_lower for word in summary_keywords):
                logger.info("Pattern match: Summary keywords detected")
                return {
                    "action": "send_message",
                    "parameters": {"body": text},
                    "confidence": 80
                }
            
            # === PATTERN 4: Help/Information ===
            help_keywords = ["help", "commands", "what can you do", "abilities", "features"]
            if any(word in text_lower for word in help_keywords):
                logger.info("Pattern match: Help keywords detected")
                return {
                    "action": "send_message",
                    "parameters": {"body": text},
                    "confidence": 85
                }
            
            # === PATTERN 5: Unsupported features (but don't error) ===
            unsupported_keywords = ["weather", "news", "sports", "jokes", "translate", "calculate", "convert"]
            if any(word in text_lower for word in unsupported_keywords):
                logger.info("Pattern match: Unsupported feature detected")
                return {
                    "action": "unsupported",
                    "parameters": {"request": text},
                    "confidence": 90
                }
            
            # === DEFAULT: Use AI only if no keywords match ===
            logger.info("No pattern match, falling back to AI")
            
            system_prompt = """You are a command parser. Determine if user wants:
- read_emails: Check/read emails
- send_email: Send an email
- schedule_task: Schedule/create task or reminder
- send_message: General message or unknown request
- unknown: Cannot determine

Reply ONLY with: {"action":"ACTION","parameters":{},"confidence":NUMBER}
Example: {"action":"read_emails","parameters":{},"confidence":85}"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                temperature=0.1,  # Very low for consistency
                max_tokens=100,
            )

            content = response.choices[0].message.content.strip()
            logger.debug(f"AI Response: {content}")
            
            # Clean markdown if present
            if "```" in content:
                content = content.split("```")[1] if len(content.split("```")) > 1 else content
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            # Parse JSON
            try:
                parsed = json.loads(content)
                action = parsed.get("action", "unknown")
                
                allowed_actions = ["read_emails", "send_email", "schedule_task", "send_message", "unknown", "unsupported"]
                if action not in allowed_actions:
                    logger.warning(f"Action '{action}' not allowed, using 'send_message'")
                    action = "send_message"
                    parsed["action"] = action
                
                parsed.setdefault("parameters", {})
                parsed.setdefault("confidence", 50)
                
                logger.info(f"Command parsed: {action} (confidence: {parsed['confidence']})")
                return parsed
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI JSON: {content} - {e}")
                # If AI response is garbage, treat as send_message
                return {
                    "action": "send_message",
                    "parameters": {"body": text},
                    "confidence": 30
                }

        except Exception as e:
            logger.error(f"Error in parse_command: {e}", exc_info=True)
            return {
                "action": "unknown",
                "parameters": {},
                "confidence": 0
            }

    def summarize_email(self, subject: str, body: str, max_length: int = 200) -> str:
        """
        Summarize an email using AI

        Args:
            subject: Email subject
            body: Email body
            max_length: Maximum summary length

        Returns:
            Email summary
        """
        try:
            system_prompt = f"""You are an email summarizer. Create a brief, concise summary of the email.
Summary should be maximum {max_length} characters.
Focus on key information and action items."""

            message_content = f"Subject: {subject}\n\nBody:\n{body}"

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message_content},
                ],
                temperature=0.5,  # Lower temperature for summaries
                max_tokens=100,
            )

            summary = response.choices[0].message.content.strip()
            logger.debug(f"Email summarized, length: {len(summary)}")
            return summary

        except Exception as e:
            logger.error(f"Failed to summarize email: {e}")
            return "[Unable to generate summary]"

    def generate_reply(
        self,
        original_subject: str,
        original_body: str,
        instruction: str,
    ) -> str:
        """
        Generate an email reply based on instruction

        Args:
            original_subject: Original email subject
            original_body: Original email body
            instruction: Instruction for reply (e.g., "say you'll get back tomorrow")

        Returns:
            Generated reply text
        """
        try:
            system_prompt = """You are an email reply generator. Generate a professional email reply.
Keep the tone friendly but professional. Do not include greeting salutation, just the body."""

            message_content = f"""Original Email:
Subject: {original_subject}
Body: {original_body}

Reply Instruction: {instruction}"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message_content},
                ],
                temperature=self.temperature,
                max_tokens=500,
            )

            reply = response.choices[0].message.content.strip()
            logger.info("Email reply generated")
            return reply

        except Exception as e:
            logger.error(f"Failed to generate reply: {e}")
            return "I'll get back to you soon."

    def classify_email_priority(self, subject: str, body: str) -> str:
        """
        Classify email priority using AI

        Args:
            subject: Email subject
            body: Email body

        Returns:
            Priority level: low, medium, high, urgent
        """
        try:
            system_prompt = """You are an email classifier. Classify the email priority as:
- low: Regular emails, newsletters, FYI
- medium: Work emails, regular updates
- high: Important work, action needed
- urgent: Time-sensitive, critical issues

Respond with ONLY the priority level, nothing else."""

            message_content = f"Subject: {subject}\n\nBody:\n{body}"

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message_content},
                ],
                temperature=0.3,  # Low temperature for classification
                max_tokens=10,
            )

            priority = response.choices[0].message.content.strip().lower()
            valid_priorities = ["low", "medium", "high", "urgent"]
            priority = priority if priority in valid_priorities else "medium"
            logger.debug(f"Email classified as: {priority}")
            return priority

        except Exception as e:
            logger.error(f"Failed to classify email: {e}")
            return "medium"

    def summarize_text(self, text: str, max_length: int = 150) -> str:
        """
        Generic text summarization

        Args:
            text: Text to summarize
            max_length: Maximum summary length

        Returns:
            Summarized text
        """
        if len(text) <= max_length:
            return text

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"Summarize the following text in maximum {max_length} characters.",
                    },
                    {"role": "user", "content": text},
                ],
                temperature=0.5,
                max_tokens=50,
            )

            summary = response.choices[0].message.content.strip()
            return summary

        except Exception as e:
            logger.error(f"Failed to summarize text: {e}")
            return text[:max_length] + "..."

    def generate_daily_summary(
        self,
        emails_count: int,
        pending_tasks: list,
        completed_tasks: list,
    ) -> str:
        """
        Generate a daily summary message

        Args:
            emails_count: Number of unread emails
            pending_tasks: List of pending tasks
            completed_tasks: List of completed tasks

        Returns:
            Formatted daily summary
        """
        try:
            content = f"""Generate a friendly daily summary with:
- {emails_count} unread emails
- Pending tasks: {', '.join(pending_tasks) if pending_tasks else 'None'}
- Completed tasks: {', '.join(completed_tasks) if completed_tasks else 'None'}

Make it motivating and concise."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a friendly daily summary generator.",
                    },
                    {"role": "user", "content": content},
                ],
                temperature=0.7,
                max_tokens=300,
            )

            summary = response.choices[0].message.content.strip()
            logger.info("Daily summary generated")
            return summary

        except Exception as e:
            logger.error(f"Failed to generate daily summary: {e}")
            return "Daily summary generation failed. Please check manually."
