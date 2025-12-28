"""Utility functions for the Personal Assistant Bot"""

import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Format datetime to readable string

    Args:
        dt: Datetime object (defaults to current time)

    Returns:
        Formatted timestamp string
    """
    if dt is None:
        dt = datetime.utcnow()
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def parse_time_string(time_str: str) -> tuple:
    """
    Parse HH:MM format time string

    Args:
        time_str: Time string in HH:MM format

    Returns:
        Tuple of (hour, minute)
    """
    try:
        parts = time_str.split(":")
        hour = int(parts[0])
        minute = int(parts[1])
        
        if not (0 <= hour < 24) or not (0 <= minute < 60):
            raise ValueError("Invalid time range")
        
        return hour, minute
    except (ValueError, IndexError) as e:
        logger.error(f"Failed to parse time string '{time_str}': {e}")
        raise ValueError(f"Invalid time format. Use HH:MM format.") from e


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to maximum length with ellipsis

    Args:
        text: Text to truncate
        max_length: Maximum length

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def extract_email_domain(email: str) -> str:
    """
    Extract domain from email address

    Args:
        email: Email address

    Returns:
        Domain part of email
    """
    try:
        return email.split("@")[1]
    except IndexError:
        return ""


def is_valid_email(email: str) -> bool:
    """
    Basic email validation

    Args:
        email: Email address to validate

    Returns:
        True if valid email format
    """
    return "@" in email and "." in email.split("@")[1]


def format_file_size(bytes_size: int) -> str:
    """
    Format bytes to human-readable size

    Args:
        bytes_size: Size in bytes

    Returns:
        Formatted size string
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_size < 1024:
            return f"{bytes_size:.1f}{unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f}TB"


def sanitize_html(text: str) -> str:
    """
    Remove HTML tags from text

    Args:
        text: Text with HTML tags

    Returns:
        Text without HTML
    """
    import re
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)


def get_initials(name: str) -> str:
    """
    Get initials from name

    Args:
        name: Full name

    Returns:
        Initials
    """
    parts = name.split()
    return "".join(p[0].upper() for p in parts if p)


def retry_with_backoff(func, max_retries: int = 3, delay: int = 2):
    """
    Retry a function with exponential backoff

    Args:
        func: Function to retry
        max_retries: Maximum retry attempts
        delay: Initial delay in seconds

    Returns:
        Function result
    """
    import time
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = delay * (2 ** attempt)
            logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
            time.sleep(wait_time)


def create_markdown_table(headers: list, rows: list) -> str:
    """
    Create markdown table

    Args:
        headers: List of column headers
        rows: List of row data (each row is a list)

    Returns:
        Markdown formatted table
    """
    md = "| " + " | ".join(headers) + " |\n"
    md += "|" + "|".join(["---"] * len(headers)) + "|\n"
    
    for row in rows:
        md += "| " + " | ".join(str(cell) for cell in row) + " |\n"
    
    return md
