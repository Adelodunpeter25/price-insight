"""Job manager for registering and managing scheduled jobs."""

from apscheduler.triggers.interval import IntervalTrigger
import logging

logger = logging.getLogger(__name__)

from app.core.scheduler import scheduler_manager
from app.ecommerce.jobs.scrape_job import scrape_tracked_products
from app.travel.jobs.travel_scrape_job import scrape_travel_prices
from app.real_estate.jobs.property_scrape_job import scrape_tracked_properties


class JobManager:
    """Manages scheduled jobs registration and monitoring."""

    def __init__(self):
        """Initialize job manager."""
        self.registered_jobs = {}

    async def register_all_jobs(self):
        """Register all application jobs."""
        logger.info("Registering scheduled jobs")

        # Register product scraping job
        await self._register_scraping_jobs()

        logger.info(f"Registered {len(self.registered_jobs)} jobs")

    async def _register_scraping_jobs(self):
        """Register product scraping jobs with different intervals."""

        # Main scraping job - every 6 hours
        job = scheduler_manager.add_job(
            func=scrape_tracked_products,
            trigger=IntervalTrigger(hours=6),
            id="scrape_products",
            name="Scrape Tracked Products",
            replace_existing=True,
        )
        self.registered_jobs["scrape_products"] = job
        logger.info("Registered product scraping job (every 6 hours)")

        # Travel scraping job - every 4 hours
        travel_job = scheduler_manager.add_job(
            func=scrape_travel_prices,
            trigger=IntervalTrigger(hours=4),
            id="scrape_travel",
            name="Scrape Travel Prices",
            replace_existing=True,
        )
        self.registered_jobs["scrape_travel"] = travel_job
        logger.info("Registered travel scraping job (every 4 hours)")

        # Real estate scraping job - every 8 hours
        property_job = scheduler_manager.add_job(
            func=scrape_tracked_properties,
            trigger=IntervalTrigger(hours=8),
            id="scrape_properties",
            name="Scrape Property Prices",
            replace_existing=True,
        )
        self.registered_jobs["scrape_properties"] = property_job
        logger.info("Registered property scraping job (every 8 hours)")

    def get_job_status(self):
        """Get status of all registered jobs."""
        jobs = scheduler_manager.get_jobs()
        status = []

        for job in jobs:
            status.append(
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                    "trigger": str(job.trigger),
                }
            )

        return status

    async def pause_job(self, job_id: str):
        """Pause a specific job."""
        try:
            scheduler_manager.scheduler.pause_job(job_id)
            logger.info(f"Paused job: {job_id}")
        except Exception as e:
            logger.error(f"Failed to pause job {job_id}: {e}")
            raise

    async def resume_job(self, job_id: str):
        """Resume a specific job."""
        try:
            scheduler_manager.scheduler.resume_job(job_id)
            logger.info(f"Resumed job: {job_id}")
        except Exception as e:
            logger.error(f"Failed to resume job {job_id}: {e}")
            raise


# Global job manager instance
job_manager = JobManager()
