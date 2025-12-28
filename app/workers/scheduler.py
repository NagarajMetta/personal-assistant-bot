"""APScheduler setup and background task management"""

import logging
from datetime import datetime
from typing import Optional, Callable, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

from app.config import get_settings

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler: Optional[AsyncIOScheduler] = None


def get_scheduler() -> AsyncIOScheduler:
    """Get or create the global scheduler instance"""
    global scheduler
    if scheduler is None:
        settings = get_settings()
        tz = timezone(settings.TIMEZONE)
        scheduler = AsyncIOScheduler(timezone=tz)
    return scheduler


async def start_scheduler():
    """Start the scheduler"""
    global scheduler
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")


async def stop_scheduler():
    """Stop the scheduler"""
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")


async def schedule_task(
    name: str,
    func: Callable,
    trigger_type: str = "cron",
    **trigger_kwargs,
) -> str:
    """
    Schedule a background task

    Args:
        name: Unique task name
        func: Async function to execute
        trigger_type: Trigger type (cron, date, interval)
        **trigger_kwargs: Trigger-specific arguments

    Returns:
        Job ID
    """
    sched = get_scheduler()
    
    try:
        if trigger_type == "cron":
            trigger = CronTrigger(**trigger_kwargs)
        elif trigger_type == "interval":
            from apscheduler.triggers.interval import IntervalTrigger
            trigger = IntervalTrigger(**trigger_kwargs)
        else:
            raise ValueError(f"Unknown trigger type: {trigger_type}")

        job = sched.add_job(
            func,
            trigger=trigger,
            id=name,
            name=name,
            replace_existing=True,
            misfire_grace_time=None,
        )
        logger.info(f"Task scheduled: {name} (ID: {job.id})")
        return job.id

    except Exception as e:
        logger.error(f"Failed to schedule task {name}: {e}")
        raise


async def schedule_once(
    name: str,
    func: Callable,
    run_time: datetime,
) -> str:
    """
    Schedule a task to run once at a specific time

    Args:
        name: Unique task name
        func: Async function to execute
        run_time: DateTime to run the task

    Returns:
        Job ID
    """
    sched = get_scheduler()
    
    try:
        from apscheduler.triggers.date import DateTrigger
        trigger = DateTrigger(run_date=run_time)
        
        job = sched.add_job(
            func,
            trigger=trigger,
            id=name,
            name=name,
            replace_existing=True,
        )
        logger.info(f"One-time task scheduled: {name} for {run_time}")
        return job.id

    except Exception as e:
        logger.error(f"Failed to schedule one-time task {name}: {e}")
        raise


async def remove_job(job_id: str) -> bool:
    """
    Remove a scheduled job

    Args:
        job_id: Job ID to remove

    Returns:
        True if successful
    """
    sched = get_scheduler()
    try:
        sched.remove_job(job_id)
        logger.info(f"Job removed: {job_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to remove job {job_id}: {e}")
        return False


def get_job(job_id: str):
    """
    Get a scheduled job by ID

    Args:
        job_id: Job ID

    Returns:
        Job object or None
    """
    sched = get_scheduler()
    return sched.get_job(job_id)


def list_jobs() -> list:
    """
    Get all scheduled jobs

    Returns:
        List of job objects
    """
    sched = get_scheduler()
    return sched.get_jobs()


async def reschedule_job(job_id: str, **trigger_kwargs) -> bool:
    """
    Reschedule an existing job with new trigger

    Args:
        job_id: Job ID to reschedule
        **trigger_kwargs: New trigger arguments

    Returns:
        True if successful
    """
    sched = get_scheduler()
    try:
        job = sched.get_job(job_id)
        if not job:
            logger.error(f"Job not found: {job_id}")
            return False

        job.reschedule(CronTrigger(**trigger_kwargs))
        logger.info(f"Job rescheduled: {job_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to reschedule job {job_id}: {e}")
        return False


async def pause_job(job_id: str) -> bool:
    """
    Pause a scheduled job

    Args:
        job_id: Job ID

    Returns:
        True if successful
    """
    sched = get_scheduler()
    try:
        job = sched.get_job(job_id)
        if job:
            job.pause()
            logger.info(f"Job paused: {job_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to pause job: {e}")
        return False


async def resume_job(job_id: str) -> bool:
    """
    Resume a paused job

    Args:
        job_id: Job ID

    Returns:
        True if successful
    """
    sched = get_scheduler()
    try:
        job = sched.get_job(job_id)
        if job:
            job.resume()
            logger.info(f"Job resumed: {job_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to resume job: {e}")
        return False
