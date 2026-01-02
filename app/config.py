"""Configuration and environment settings"""

import os
import logging
from pathlib import Path
from typing import Optional
from functools import lru_cache
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

# Project root
PROJECT_ROOT = Path(__file__).parent.parent


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # App
    APP_NAME: str = "Personal Assistant Bot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Server
    SERVER_HOST: str = "0.0.0.0"  # Allow external connections for cloud
    SERVER_PORT: int = int(os.environ.get("PORT", 8000))  # Railway sets PORT

    # Database
    DATABASE_URL: str = "sqlite:///./bot_database.db"
    DATABASE_PATH: Path = PROJECT_ROOT / "bot_database.db"

    # Gmail API
    GMAIL_ENABLED: bool = False
    GMAIL_CREDENTIALS_FILE: str = "credentials.json"
    GMAIL_TOKEN_FILE: str = "token.json"
    GMAIL_SCOPES: list = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
    ]

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""  # Required - set in Railway Variables
    TELEGRAM_WEBHOOK_URL: Optional[str] = None
    TELEGRAM_WEBHOOK_SECRET: str = "your-secret-key"
    TELEGRAM_USER_ID: int = 0  # Required - set in Railway Variables

    # OpenAI
    OPENAI_API_KEY: str = ""  # Required - set in Railway Variables
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 1000

    # Scheduler
    SCHEDULER_ENABLED: bool = True
    MORNING_SUMMARY_TIME: str = "08:00"  # HH:MM format
    EVENING_SUMMARY_TIME: str = "20:00"
    TIMEZONE: str = "UTC"

    # Email preferences
    EMAIL_CHECK_INTERVAL: int = 300  # 5 minutes
    SUMMARIZE_EMAILS: bool = True
    AUTO_REPLY_ENABLED: bool = False

    # Logging
    LOG_FILE: Path = PROJECT_ROOT / "logs" / "bot.log"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Retry settings
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 5  # seconds

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @property
    def database_url_async(self) -> str:
        """Get async SQLAlchemy connection string"""
        return self.DATABASE_URL.replace("sqlite", "sqlite+aiosqlite", 1)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


def setup_logging(settings: Settings) -> None:
    """Configure logging for the application"""
    # For cloud deployment, use stdout only (no file)
    if os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("PORT"):
        logging.basicConfig(
            level=getattr(logging, settings.LOG_LEVEL),
            format=settings.LOG_FORMAT,
            handlers=[logging.StreamHandler()],
        )
        logger.info("Cloud deployment detected - logging to stdout")
    else:
        # Local development - use file and stdout
        settings.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=getattr(logging, settings.LOG_LEVEL),
            format=settings.LOG_FORMAT,
            handlers=[
                logging.FileHandler(settings.LOG_FILE),
                logging.StreamHandler(),
            ],
        )
        logger.info(f"Logging configured at level: {settings.LOG_LEVEL}")
        logger.info(f"Log file location: {settings.LOG_FILE}")


# Validate required settings on import
def validate_settings(settings: Settings) -> None:
    """Validate critical settings are configured"""
    required = {
        "TELEGRAM_BOT_TOKEN": "Telegram bot token",
        "OPENAI_API_KEY": "OpenAI API key",
        "TELEGRAM_USER_ID": "Your Telegram user ID",
    }

    missing = []
    for field, description in required.items():
        if not getattr(settings, field, None):
            missing.append(f"{field} ({description})")

    if missing:
        raise ValueError(
            f"Missing required environment variables:\n" + "\n".join(missing)
        )
