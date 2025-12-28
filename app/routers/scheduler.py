"""Task scheduling and job management router"""

import logging
from typing import List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.schemas import ScheduleRequest, TaskSchema, TaskCreate
from app.models.database import get_db, Task, ScheduledJob, TaskStatus
from app.workers import scheduler
from app.workers.tasks import (
    check_emails,
    send_daily_summary,
    process_scheduled_tasks,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/scheduler", tags=["scheduler"])

settings = get_settings()


@router.post("/start")
async def start_scheduler_endpoint() -> dict:
    """Start the background scheduler"""
    try:
        await scheduler.start_scheduler()
        return {"status": "started"}
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_scheduler_endpoint() -> dict:
    """Stop the background scheduler"""
    try:
        await scheduler.stop_scheduler()
        return {"status": "stopped"}
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schedule", response_model=dict)
async def schedule_task(request: ScheduleRequest, db: Session = Depends(get_db)) -> dict:
    """
    Schedule a new task

    Args:
        request: Schedule request
        db: Database session

    Returns:
        Scheduled job details
    """
    try:
        # Save to database
        job = ScheduledJob(
            name=request.task_name,
            job_type=request.job_type,
            schedule_time=request.schedule_time,
            cron_expression=request.cron_expression,
        )
        db.add(job)
        db.commit()

        # Schedule the actual job
        if request.job_type == "daily" and request.schedule_time:
            hour, minute = request.schedule_time.split(":")
            job_id = await scheduler.schedule_task(
                request.task_name,
                check_emails,
                trigger_type="cron",
                hour=int(hour),
                minute=int(minute),
            )
        elif request.job_type == "custom" and request.cron_expression:
            job_id = await scheduler.schedule_task(
                request.task_name,
                check_emails,
                trigger_type="cron",
                **_parse_cron(request.cron_expression),
            )
        else:
            job_id = request.task_name

        logger.info(f"Task scheduled: {request.task_name}")
        return {
            "status": "scheduled",
            "job_id": job_id,
            "task_name": request.task_name,
            "job_type": request.job_type,
        }

    except Exception as e:
        logger.error(f"Error scheduling task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs")
async def list_scheduled_jobs() -> dict:
    """
    Get list of all scheduled jobs

    Returns:
        List of scheduled jobs
    """
    try:
        jobs = scheduler.list_jobs()
        job_list = []

        for job in jobs:
            job_list.append(
                {
                    "id": job.id,
                    "name": job.name,
                    "trigger": str(job.trigger),
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                }
            )

        return {"jobs": job_list, "count": len(job_list)}

    except Exception as e:
        logger.error(f"Error listing jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/jobs/{job_id}")
async def remove_scheduled_job(job_id: str) -> dict:
    """
    Remove a scheduled job

    Args:
        job_id: Job ID to remove

    Returns:
        Removal status
    """
    try:
        success = await scheduler.remove_job(job_id)
        return {"status": "removed" if success else "not_found"}
    except Exception as e:
        logger.error(f"Error removing job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/jobs/{job_id}/pause")
async def pause_scheduled_job(job_id: str) -> dict:
    """
    Pause a scheduled job

    Args:
        job_id: Job ID to pause

    Returns:
        Operation status
    """
    try:
        success = await scheduler.pause_job(job_id)
        return {"status": "paused" if success else "failed"}
    except Exception as e:
        logger.error(f"Error pausing job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/jobs/{job_id}/resume")
async def resume_scheduled_job(job_id: str) -> dict:
    """
    Resume a paused job

    Args:
        job_id: Job ID to resume

    Returns:
        Operation status
    """
    try:
        success = await scheduler.resume_job(job_id)
        return {"status": "resumed" if success else "failed"}
    except Exception as e:
        logger.error(f"Error resuming job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-now/{job_id}")
async def run_job_now(job_id: str) -> dict:
    """
    Run a scheduled job immediately

    Args:
        job_id: Job ID to run

    Returns:
        Execution result
    """
    try:
        if job_id == "check_emails":
            result = await check_emails()
        elif job_id == "daily_summary":
            result = await send_daily_summary()
        else:
            result = {"status": "unknown_job"}

        return result

    except Exception as e:
        logger.error(f"Error running job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks", response_model=TaskSchema)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)) -> Task:
    """
    Create a new task

    Args:
        task: Task data
        db: Database session

    Returns:
        Created task
    """
    try:
        db_task = Task(
            name=task.name,
            description=task.description,
            command=task.command,
            scheduled_time=task.scheduled_time,
            status=TaskStatus.PENDING,
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)

        logger.info(f"Task created: {task.name}")
        return db_task

    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks", response_model=List[TaskSchema])
async def list_tasks(
    status: str = None, db: Session = Depends(get_db)
) -> List[Task]:
    """
    List tasks with optional filtering

    Args:
        status: Optional status filter
        db: Database session

    Returns:
        List of tasks
    """
    try:
        query = db.query(Task)

        if status:
            query = query.filter(Task.status == status)

        tasks = query.order_by(Task.created_at.desc()).all()
        return tasks

    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}", response_model=TaskSchema)
async def get_task(task_id: int, db: Session = Depends(get_db)) -> Task:
    """
    Get a specific task

    Args:
        task_id: Task ID
        db: Database session

    Returns:
        Task details
    """
    try:
        task = db.query(Task).filter(Task.id == task_id).first()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        return task

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _parse_cron(cron_expression: str) -> dict:
    """
    Parse cron expression to APScheduler format

    Args:
        cron_expression: Cron expression string

    Returns:
        Dictionary of trigger parameters
    """
    parts = cron_expression.split()
    if len(parts) < 5:
        return {}

    return {
        "minute": parts[0],
        "hour": parts[1],
        "day": parts[2],
        "month": parts[3],
        "day_of_week": parts[4],
    }
