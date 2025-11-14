"""Scheduled scraping jobs for all categories."""

import logging
from datetime import datetime
from typing import Dict

from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger(__name__)

from app.core.database import get_db
from app.core.scraping.scraper_manager import scraper_manager
from app.travel.services.deal_detector import TravelDealDetector


class ScrapingJobScheduler:
    """Scheduler for automated scraping jobs."""

    def __init__(self):
        """Initialize scheduler."""
        self.scheduler = AsyncIOScheduler()
        self.is_running = False

    def start(self):
        """Start the scheduler."""
        if not self.is_running:
            self._schedule_jobs()
            self.scheduler.start()
            self.is_running = True
            logger.info("Scraping job scheduler started")

    def stop(self):
        """Stop the scheduler."""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Scraping job scheduler stopped")

    def _schedule_jobs(self):
        """Schedule all scraping jobs."""
        # E-commerce products - every 2 hours
        self.scheduler.add_job(
            self._scrape_ecommerce_job,
            "interval",
            hours=2,
            id="scrape_ecommerce",
            name="Scrape E-commerce Products",
        )

        # Travel deals - every 4 hours
        self.scheduler.add_job(
            self._scrape_travel_job,
            "interval",
            hours=4,
            id="scrape_travel",
            name="Scrape Travel Deals",
        )

        # Real estate - every 6 hours
        self.scheduler.add_job(
            self._scrape_real_estate_job,
            "interval",
            hours=6,
            id="scrape_real_estate",
            name="Scrape Real Estate Properties",
        )

        # Utilities - every 12 hours
        self.scheduler.add_job(
            self._scrape_utilities_job,
            "interval",
            hours=12,
            id="scrape_utilities",
            name="Scrape Utility Services",
        )

        # Comprehensive scraping - daily at 2 AM
        self.scheduler.add_job(
            self._comprehensive_scrape_job,
            "cron",
            hour=2,
            minute=0,
            id="comprehensive_scrape",
            name="Comprehensive Daily Scrape",
        )

    async def _scrape_ecommerce_job(self):
        """Scheduled job for e-commerce scraping."""
        logger.info("Starting scheduled e-commerce scraping")
        try:
            db = next(get_db())
            updated_count = await scraper_manager.scrape_ecommerce_products(db)
            logger.info(f"E-commerce scraping completed: {updated_count} products updated")
        except Exception as e:
            logger.error(f"E-commerce scraping job failed: {e}")
        finally:
            db.close()

    async def _scrape_travel_job(self):
        """Scheduled job for travel scraping and deal detection."""
        logger.info("Starting scheduled travel scraping")
        try:
            db = next(get_db())

            # Scrape travel deals
            updated_count = await scraper_manager.scrape_travel_deals(db)
            logger.info(f"Travel scraping completed: {updated_count} deals updated")

            # Run deal detection
            deal_detector = TravelDealDetector()
            detected_deals = deal_detector.detect_deals(db)
            logger.info(f"Travel deal detection completed: {len(detected_deals)} deals detected")

            db.commit()

        except Exception as e:
            logger.error(f"Travel scraping job failed: {e}")
            db.rollback()
        finally:
            db.close()

    async def _scrape_real_estate_job(self):
        """Scheduled job for real estate scraping."""
        logger.info("Starting scheduled real estate scraping")
        try:
            db = next(get_db())
            updated_count = await scraper_manager.scrape_real_estate_properties(db)
            logger.info(f"Real estate scraping completed: {updated_count} properties updated")
        except Exception as e:
            logger.error(f"Real estate scraping job failed: {e}")
        finally:
            db.close()

    async def _scrape_utilities_job(self):
        """Scheduled job for utilities scraping."""
        logger.info("Starting scheduled utilities scraping")
        try:
            db = next(get_db())
            updated_count = await scraper_manager.scrape_utility_services(db)
            logger.info(f"Utilities scraping completed: {updated_count} services updated")
        except Exception as e:
            logger.error(f"Utilities scraping job failed: {e}")
        finally:
            db.close()

    async def _comprehensive_scrape_job(self):
        """Comprehensive daily scraping job."""
        logger.info("Starting comprehensive daily scraping")
        try:
            db = next(get_db())
            results = await scraper_manager.scrape_all_categories(db)

            total_updated = sum(results.values())
            logger.info(f"Comprehensive scraping completed: {total_updated} total items updated")
            logger.info(f"Breakdown: {results}")

        except Exception as e:
            logger.error(f"Comprehensive scraping job failed: {e}")
        finally:
            db.close()

    def trigger_manual_scrape(self, category: str = "all"):
        """Trigger manual scraping for specific category."""
        if category == "all":
            self.scheduler.add_job(
                self._comprehensive_scrape_job,
                "date",
                run_date=datetime.now(),
                id=f"manual_scrape_all_{datetime.now().timestamp()}",
                name="Manual Comprehensive Scrape",
            )
        elif category == "ecommerce":
            self.scheduler.add_job(
                self._scrape_ecommerce_job,
                "date",
                run_date=datetime.now(),
                id=f"manual_scrape_ecommerce_{datetime.now().timestamp()}",
                name="Manual E-commerce Scrape",
            )
        elif category == "travel":
            self.scheduler.add_job(
                self._scrape_travel_job,
                "date",
                run_date=datetime.now(),
                id=f"manual_scrape_travel_{datetime.now().timestamp()}",
                name="Manual Travel Scrape",
            )
        elif category == "real_estate":
            self.scheduler.add_job(
                self._scrape_real_estate_job,
                "date",
                run_date=datetime.now(),
                id=f"manual_scrape_real_estate_{datetime.now().timestamp()}",
                name="Manual Real Estate Scrape",
            )
        elif category == "utilities":
            self.scheduler.add_job(
                self._scrape_utilities_job,
                "date",
                run_date=datetime.now(),
                id=f"manual_scrape_utilities_{datetime.now().timestamp()}",
                name="Manual Utilities Scrape",
            )
        else:
            logger.warning(f"Unknown category for manual scrape: {category}")

    def get_job_status(self) -> Dict:
        """Get status of all scheduled jobs."""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append(
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                    "trigger": str(job.trigger),
                }
            )

        return {"scheduler_running": self.is_running, "jobs": jobs}


# Global scheduler instance
scraping_scheduler = ScrapingJobScheduler()
