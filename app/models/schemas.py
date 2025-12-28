"""Pydantic schemas for API requests and responses"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


class TaskCreate(BaseModel):
    """Schema for creating a new task"""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    command: str = Field(..., min_length=1)
    scheduled_time: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Morning Email Check",
                "description": "Read and summarize unread emails",
                "command": "read_unread_emails",
                "scheduled_time": "2024-01-15T08:00:00",
            }
        }


class TaskUpdate(BaseModel):
    """Schema for updating a task"""

    name: Optional[str] = None
    description: Optional[str] = None
    command: Optional[str] = None
    scheduled_time: Optional[datetime] = None


class TaskSchema(TaskCreate):
    """Full task schema with database fields"""

    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class EmailSchema(BaseModel):
    """Schema for email data"""

    id: Optional[int] = None
    gmail_id: str
    sender: str
    subject: str
    body: str
    summary: Optional[str] = None
    priority: str = "medium"
    is_unread: bool = True
    is_replied: bool = False
    received_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "gmail_id": "abc123",
                "sender": "john@example.com",
                "subject": "Meeting Tomorrow",
                "body": "Hi, let's meet tomorrow at 2pm",
                "priority": "high",
                "received_at": "2024-01-15T10:30:00",
            }
        }


class MessageSchema(BaseModel):
    """Schema for Telegram message"""

    telegram_message_id: str
    user_id: int
    text: str
    command: Optional[str] = None
    response: Optional[str] = None
    is_command: bool = False

    class Config:
        from_attributes = True


class CommandRequest(BaseModel):
    """Schema for natural language command requests"""

    text: str = Field(..., min_length=1)
    user_id: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Send an email to john@example.com saying hello",
                "user_id": 123456,
            }
        }


class ScheduleRequest(BaseModel):
    """Schema for scheduling a task"""

    task_name: str
    command: str
    schedule_time: Optional[str] = None  # HH:MM format
    cron_expression: Optional[str] = None
    job_type: str = "once"  # once, daily, weekly, custom

    class Config:
        json_schema_extra = {
            "example": {
                "task_name": "Morning Summary",
                "command": "send_morning_summary",
                "schedule_time": "08:00",
                "job_type": "daily",
            }
        }


class TelegramUpdate(BaseModel):
    """Schema for Telegram webhook update"""

    update_id: int
    message: Optional[dict] = None


class HealthCheck(BaseModel):
    """Schema for health check response"""

    status: str = "ok"
    version: str
    timestamp: datetime
