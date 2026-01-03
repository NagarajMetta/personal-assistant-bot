"""Main FastAPI application entry point"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings, setup_logging, validate_settings
from app.models.database import init_db
from app.models.schemas import HealthCheck
from app.routers import telegram, scheduler, email
from app.workers.scheduler import start_scheduler, stop_scheduler
from app import __version__

# Configure logging
settings = get_settings()
setup_logging(settings)
logger = logging.getLogger(__name__)

# Validate required settings
try:
    validate_settings(settings)
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle startup and shutdown events

    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    # Start scheduler
    if settings.SCHEDULER_ENABLED:
        try:
            await start_scheduler()
            logger.info("Scheduler started successfully")
        except Exception as e:
            logger.warning(f"Failed to start scheduler: {e}")

    yield

    # Shutdown
    logger.info("Shutting down application")
    
    try:
        await stop_scheduler()
        logger.info("Scheduler stopped")
    except Exception as e:
        logger.warning(f"Error stopping scheduler: {e}")

    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Intelligent Personal Assistant Bot for automating daily tasks",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/", response_model=HealthCheck)
async def root() -> HealthCheck:
    """
    Root endpoint providing API health check

    Returns:
        Health check response
    """
    return HealthCheck(
        status="ok",
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow(),
    )


# Health check endpoint
@app.get("/health", response_model=dict)
async def health_check() -> dict:
    """
    Detailed health check endpoint

    Returns:
        Health status details
    """
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG,
        "timezone": settings.TIMEZONE,
        "scheduler_enabled": settings.SCHEDULER_ENABLED,
        "timestamp": datetime.utcnow().isoformat(),
    }


# Include routers
app.include_router(telegram.router)

# Only include email router if Gmail is enabled
if settings.GMAIL_ENABLED:
    app.include_router(email.router)
else:
    logger.info("Gmail operations disabled - email router not loaded")

app.include_router(scheduler.router)


# API documentation endpoints
@app.get("/api/docs", tags=["documentation"])
async def api_documentation() -> dict:
    """
    API documentation and available endpoints

    Returns:
        API endpoints information
    """
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "endpoints": {
            "telegram": {
                "webhook": "POST /telegram/webhook - Receive Telegram updates",
                "command": "POST /telegram/command - Execute a command",
                "send": "POST /telegram/send - Send a message",
                "status": "GET /telegram/status - Get bot status",
            },
            "email": {
                "unread": "GET /email/unread - Get unread emails",
                "inbox": "GET /email/inbox - Get inbox emails",
                "send": "POST /email/send - Send an email",
                "draft": "POST /email/draft - Create a draft",
                "summary": "GET /email/summary/{id} - Get email summary",
                "mark_read": "POST /email/mark-read/{id} - Mark as read",
            },
            "scheduler": {
                "start": "POST /scheduler/start - Start scheduler",
                "stop": "POST /scheduler/stop - Stop scheduler",
                "schedule": "POST /scheduler/schedule - Schedule a task",
                "jobs": "GET /scheduler/jobs - List scheduled jobs",
                "run_job": "POST /scheduler/run-now/{job_id} - Run job now",
                "tasks": "POST /scheduler/tasks - Create task",
                "list_tasks": "GET /scheduler/tasks - List tasks",
            },
        },
        "environment": {
            "debug": settings.DEBUG,
            "log_level": settings.LOG_LEVEL,
            "timezone": settings.TIMEZONE,
            "scheduler_enabled": settings.SCHEDULER_ENABLED,
        },
    }


@app.get("/api/info", tags=["documentation"])
async def api_info() -> dict:
    """
    Get application information

    Returns:
        Application info
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Personal Assistant Bot - Automates daily tasks with AI",
        "features": [
            "Email automation with Gmail API",
            "Telegram bot for commands and messages",
            "Task scheduling and automation",
            "AI-powered command parsing and email summarization",
            "Daily routine management",
        ],
        "endpoints": "/api/docs",
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return {
        "error": exc.detail,
        "status_code": exc.status_code,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return {
        "error": "Internal server error",
        "status_code": 500,
        "timestamp": datetime.utcnow().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
