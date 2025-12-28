"""Database models and ORM setup"""

from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import enum

from app.config import get_settings

# Initialize base for ORM models
Base = declarative_base()

# Create database settings
settings = get_settings()


class TaskStatus(str, enum.Enum):
    """Task status enumeration"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EmailPriority(str, enum.Enum):
    """Email priority levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(Base):
    """Scheduled task model"""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    command = Column(Text, nullable=False)  # Natural language command or task
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    scheduled_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Task(id={self.id}, name={self.name}, status={self.status})>"


class Email(Base):
    """Email message model"""

    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    gmail_id = Column(String(255), unique=True, index=True)
    sender = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    priority = Column(Enum(EmailPriority), default=EmailPriority.MEDIUM)
    is_unread = Column(Boolean, default=True)
    is_replied = Column(Boolean, default=False)
    received_at = Column(DateTime, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Email(id={self.id}, from={self.sender}, subject={self.subject[:50]})>"


class Message(Base):
    """Telegram message model"""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    telegram_message_id = Column(String(255), unique=True, index=True)
    user_id = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    command = Column(String(255), nullable=True)
    response = Column(Text, nullable=True)
    is_command = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Message(id={self.id}, user={self.user_id}, text={self.text[:50]})>"


class ScheduledJob(Base):
    """Scheduled job model for recurring tasks"""

    __tablename__ = "scheduled_jobs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    job_type = Column(String(50), nullable=False)  # "daily", "weekly", "custom"
    schedule_time = Column(String(10), nullable=True)  # HH:MM format
    cron_expression = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    is_enabled = Column(Boolean, default=True)
    last_run = Column(DateTime, nullable=True)
    next_run = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ScheduledJob(id={self.id}, name={self.name}, type={self.job_type})>"


# Database engine and session
engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
