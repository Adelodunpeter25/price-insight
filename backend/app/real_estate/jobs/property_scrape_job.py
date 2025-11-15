"""Property scraping job for real estate price tracking."""

import asyncio
import logging
from typing import Dict, List

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.scraping.scraper_manager import scraper_manager
from app.real_estate.models.property import Property
from app.real_estate.services.deal_detector import RealEstateDealDetector
from app.real_estate.services.watchlist_alerts import PropertyWatchlistAlerts

logger = logging.getLogger(__name__)


async def scrape_tracked_properties():
    """Main property scraping job that processes all tracked properties."""
    logger.info("Starting property scraping job")

    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(Property).where(Property.is_active == True, Property.is_tracked == 1)
            )
            properties = result.scalars().all()

            if not properties:
                logger.info("No properties to track")
                return

            logger.info(f"Found {len(properties)} properties to scrape")
            updated_count = await scraper_manager.scrape_real_estate_properties(db)
            logger.info(f"Property scraping completed: {updated_count} properties updated")

        except Exception as e:
            logger.error(f"Property scraping job failed: {e}")
            raise


async def detect_property_deals():
    """Detect property deals based on price history."""
    logger.info("Starting property deal detection")

    async with AsyncSessionLocal() as db:
        try:
            detector = RealEstateDealDetector()
            deals = detector.detect_deals(db)
            logger.info(f"Property deal detection completed: {len(deals)} deals found")

        except Exception as e:
            logger.error(f"Property deal detection failed: {e}")
            raise


async def check_property_watchlist_alerts():
    """Check watchlist items and send alerts."""
    logger.info("Starting property watchlist alert check")

    async with AsyncSessionLocal() as db:
        try:
            alerts_sent = await PropertyWatchlistAlerts.check_watchlist_alerts(db)
            logger.info(f"Property watchlist alerts completed: {alerts_sent} alerts sent")

        except Exception as e:
            logger.error(f"Property watchlist alert check failed: {e}")
            raise


def _group_properties_by_site(properties: List[Property]) -> Dict[str, List[Property]]:
    """Group properties by site for efficient scraping."""
    grouped = {}
    for property_obj in properties:
        site = property_obj.site
        if site not in grouped:
            grouped[site] = []
        grouped[site].append(property_obj)
    return grouped
