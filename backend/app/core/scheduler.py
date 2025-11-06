"""APScheduler configuration and management."""

from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

from app.core.config import settings


class SchedulerManager:
    """Manages APScheduler instance and job lifecycle."""

    def __init__(self):
        """Initialize scheduler with configuration."""
        jobstores = {"default": MemoryJobStore()}

        executors = {"default": AsyncIOExecutor()}

        job_defaults = {"coalesce": False, "max_instances": 3}

        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone="UTC"
        )

        self._is_running = False

    async def start(self):
        """Start the scheduler."""
        if not self._is_running:
            self.scheduler.start()
            self._is_running = True
            logger.info("Scheduler started successfully")

    async def shutdown(self):
        """Shutdown the scheduler gracefully."""
        if self._is_running:
            self.scheduler.shutdown(wait=True)
            self._is_running = False
            logger.info("Scheduler shutdown completed")

    def add_job(self, func, trigger, **kwargs):
        """Add a job to the scheduler."""
        return self.scheduler.add_job(func, trigger, **kwargs)

    def get_jobs(self):
        """Get all scheduled jobs."""
        return self.scheduler.get_jobs()

    @property
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._is_running


# Global scheduler instance
scheduler_manager = SchedulerManager()
