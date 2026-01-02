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
            
            # === PATTERN 0: Real-time data queries - CHECK FIRST! ===
            
            # Stock price queries
            stock_keywords = ["stock", "share price", "stock price", "ticker", "market price"]
            if any(word in text_lower for word in stock_keywords):
                logger.info("Pattern match: Stock price query detected")
                # Extract stock symbol - look for common patterns
                words = text.upper().split()
                symbol = None
                for i, word in enumerate(words):
                    # Look for word after "stock" or standalone ticker symbols
                    clean_word = ''.join(c for c in word if c.isalpha())
                    if clean_word in ["AAPL", "GOOGL", "GOOG", "MSFT", "AMZN", "META", "TSLA", "NVDA", "NFLX", "AMD", "INTC", "IBM", "ORCL", "CRM", "ADBE", "PYPL", "UBER", "LYFT", "SPOT", "SNAP", "TWTR", "PINS", "ZM", "SHOP", "SQ", "COIN", "HOOD", "RBLX", "ABNB", "PLTR", "SOFI", "NIO", "RIVN", "LCID", "F", "GM", "TM", "BA", "DIS", "WMT", "TGT", "COST", "HD", "LOW", "NKE", "SBUX", "MCD", "KO", "PEP", "JNJ", "PFE", "MRNA", "BNTX", "UNH", "CVS", "WBA", "JPM", "BAC", "WFC", "C", "GS", "MS", "V", "MA", "AXP"]:
                        symbol = clean_word
                        break
                    # Check if previous word was "stock" or similar
                    if i > 0 and any(kw in words[i-1].lower() for kw in ["stock", "price", "ticker"]):
                        if len(clean_word) <= 5 and clean_word.isalpha():
                            symbol = clean_word
                            break
                
                if not symbol:
                    # Try to find any word that looks like a ticker (2-5 uppercase letters)
                    for word in words:
                        clean_word = ''.join(c for c in word if c.isalpha())
                        if 1 <= len(clean_word) <= 5 and clean_word.isalpha() and clean_word not in ["THE", "AND", "FOR", "WHAT", "PRICE", "STOCK", "SHOW", "GET", "CHECK"]:
                            symbol = clean_word
                            break
                
                return {
                    "action": "get_stock_price",
                    "parameters": {"symbol": symbol or "AAPL"},
                    "confidence": 95
                }
            
            # Cryptocurrency queries
            crypto_keywords = ["bitcoin", "btc", "ethereum", "eth", "crypto", "cryptocurrency", "dogecoin", "doge", "solana", "sol", "cardano", "ada", "ripple", "xrp"]
            if any(word in text_lower for word in crypto_keywords):
                logger.info("Pattern match: Cryptocurrency query detected")
                # Map keywords to symbols
                symbol = "BTC"  # default
                if "ethereum" in text_lower or "eth" in text_lower.split():
                    symbol = "ETH"
                elif "dogecoin" in text_lower or "doge" in text_lower:
                    symbol = "DOGE"
                elif "solana" in text_lower or "sol" in text_lower.split():
                    symbol = "SOL"
                elif "cardano" in text_lower or "ada" in text_lower.split():
                    symbol = "ADA"
                elif "ripple" in text_lower or "xrp" in text_lower:
                    symbol = "XRP"
                
                return {
                    "action": "get_crypto_price",
                    "parameters": {"symbol": symbol},
                    "confidence": 95
                }
            
            # Time in city queries
            time_keywords = ["time in", "current time in", "what time", "time now in", "local time"]
            if any(word in text_lower for word in time_keywords):
                logger.info("Pattern match: Time query detected")
                # Extract city name
                city = "New York"  # default
                # Common patterns: "time in Tokyo", "what time is it in London"
                for pattern in ["time in ", "time is it in ", "time now in "]:
                    if pattern in text_lower:
                        city = text_lower.split(pattern)[-1].strip().rstrip("?").strip()
                        break
                
                return {
                    "action": "get_time",
                    "parameters": {"city": city},
                    "confidence": 95
                }
            
            # Weather queries
            weather_keywords = ["weather in", "weather at", "temperature in", "forecast", "how hot", "how cold", "is it raining", "weather today"]
            if any(word in text_lower for word in weather_keywords):
                logger.info("Pattern match: Weather query detected")
                # Extract city name
                city = "New York"  # default
                for pattern in ["weather in ", "weather at ", "temperature in ", "forecast for ", "forecast in "]:
                    if pattern in text_lower:
                        city = text_lower.split(pattern)[-1].strip().rstrip("?").strip()
                        break
                
                return {
                    "action": "get_weather",
                    "parameters": {"city": city},
                    "confidence": 95
                }
            
            # === PATTERN 1: General Questions (Q&A) ===
            # This catches most natural language queries
            question_indicators = ["what", "who", "where", "when", "why", "how", "tell me", "explain", "describe", "?", "meaning", "define", "capital", "population", "distance", "calculate", "convert"]
            if any(indicator in text_lower for indicator in question_indicators):
                logger.info("Pattern match: General question detected - routing to Q&A")
                return {
                    "action": "ask_question",
                    "parameters": {"question": text},
                    "confidence": 90
                }
            
            # === PATTERN 2: Email related ===
            email_keywords = ["email", "mail", "unread", "inbox", "gmail"]
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
            
            # === PATTERN 3: Task/Schedule related ===
            task_keywords = ["task", "todo", "reminder", "schedule", "remind", "alarm", "meeting", "appointment"]
            if any(word in text_lower for word in task_keywords):
                logger.info("Pattern match: Task/schedule keywords detected")
                return {
                    "action": "schedule_task",
                    "parameters": {"task_name": text},
                    "confidence": 85
                }
            
            # === PATTERN 4: Summary related ===
            summary_keywords = ["summary", "daily summary", "overview", "report", "briefing"]
            if any(word in text_lower for word in summary_keywords):
                logger.info("Pattern match: Summary keywords detected")
                return {
                    "action": "send_message",
                    "parameters": {"body": text},
                    "confidence": 80
                }
            
            # === PATTERN 5: Help/Information ===
            help_keywords = ["help", "commands", "what can you do", "abilities", "features"]
            if any(word in text_lower for word in help_keywords):
                logger.info("Pattern match: Help keywords detected")
                return {
                    "action": "send_message",
                    "parameters": {"body": text},
                    "confidence": 85
                }
            
            # === DEFAULT: Treat everything else as a question ===
            logger.info("No specific pattern match - treating as general question")
            return {
                "action": "ask_question",
                "parameters": {"question": text},
                "confidence": 75
            }

        except Exception as e:
            logger.error(f"Error in parse_command: {e}", exc_info=True)
            return {
                "action": "ask_question",
                "parameters": {"question": text},
                "confidence": 50
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

    def answer_question(self, question: str) -> str:
        """
        Answer a general question using OpenAI (real-time Q&A)

        Args:
            question: User's question

        Returns:
            AI-generated answer
        """
        try:
            logger.info(f"Answering question: {question}")
            
            system_prompt = """You are a helpful personal assistant. Answer questions concisely and accurately.
If asked about real-time data (weather, stock prices, current news), explain that you don't have access to real-time data but provide helpful general information.
Keep responses brief but informative (max 200 words).
Use emojis to make responses friendly."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question},
                ],
                temperature=0.7,
                max_tokens=500,
            )

            answer = response.choices[0].message.content.strip()
            logger.info(f"Question answered successfully")
            return answer

        except Exception as e:
            logger.error(f"Failed to answer question: {e}")
            return "❌ Sorry, I couldn't process your question. Please try again."

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
