"""Celery tasks for distributed scraping."""

import asyncio
import logging
from typing import List

from celery import group

from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.core.scraping.scraper_manager import scraper_manager
from app.travel.models.flight import Flight
from app.travel.models.hotel import Hotel
from app.ecommerce.models.product import Product
from sqlalchemy import select

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def scrape_url_task(self, url: str, category: str = "auto"):
    """Scrape single URL as distributed task."""
    try:
        result = asyncio.run(_scrape_url_async(url, category))
        return result
    except Exception as e:
        logger.error(f"Failed to scrape {url}: {e}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task(bind=True)
def scrape_ecommerce_batch(self, urls: List[str]):
    """Scrape batch of e-commerce URLs."""
    try:
        return asyncio.run(_scrape_batch_async(urls, "ecommerce"))
    except Exception as e:
        logger.error(f"Batch scraping failed: {e}")
        raise self.retry(exc=e, countdown=120)


@celery_app.task(bind=True)
def scrape_travel_batch(self, urls: List[str]):
    """Scrape batch of travel URLs."""
    try:
        return asyncio.run(_scrape_batch_async(urls, "travel"))
    except Exception as e:
        logger.error(f"Travel batch scraping failed: {e}")
        raise self.retry(exc=e, countdown=120)


@celery_app.task(bind=True)
def scrape_real_estate_batch(self, urls: List[str]):
    """Scrape batch of real estate URLs."""
    try:
        return asyncio.run(_scrape_batch_async(urls, "real_estate"))
    except Exception as e:
        logger.error(f"Real estate batch scraping failed: {e}")
        raise self.retry(exc=e, countdown=120)


@celery_app.task(bind=True)
def scrape_utilities_batch(self, urls: List[str]):
    """Scrape batch of utility URLs."""
    try:
        return asyncio.run(_scrape_batch_async(urls, "utilities"))
    except Exception as e:
        logger.error(f"Utilities batch scraping failed: {e}")
        raise self.retry(exc=e, countdown=120)


@celery_app.task
def scrape_all_ecommerce():
    """Distribute e-commerce scraping across workers."""
    return asyncio.run(_distribute_ecommerce_scraping())


@celery_app.task
def scrape_all_travel():
    """Distribute travel scraping across workers."""
    return asyncio.run(_distribute_travel_scraping())


@celery_app.task
def scrape_all_real_estate():
    """Distribute real estate scraping across workers."""
    return asyncio.run(_distribute_real_estate_scraping())


@celery_app.task
def scrape_all_utilities():
    """Distribute utilities scraping across workers."""
    return asyncio.run(_distribute_utilities_scraping())


async def _scrape_url_async(url: str, category: str):
    """Async helper for scraping single URL."""
    return await scraper_manager.scrape_url(url, category)


async def _scrape_batch_async(urls: List[str], category: str):
    """Async helper for scraping batch of URLs."""
    return await scraper_manager.scrape_multiple(urls, category)


async def _distribute_ecommerce_scraping():
    """Distribute e-commerce scraping to multiple workers."""
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Product.url).where(Product.is_active == True)
        )
        urls = [row[0] for row in result.all()]
    
    if not urls:
        return {"status": "no_products", "count": 0}
    
    # Split into batches for distribution
    batch_size = 20
    batches = [urls[i:i + batch_size] for i in range(0, len(urls), batch_size)]
    
    # Create distributed tasks
    job = group(scrape_ecommerce_batch.s(batch) for batch in batches)
    result = job.apply_async()
    
    return {
        "status": "distributed",
        "total_urls": len(urls),
        "batches": len(batches),
        "task_id": result.id
    }


async def _distribute_travel_scraping():
    """Distribute travel scraping to multiple workers."""
    async with AsyncSessionLocal() as db:
        flight_result = await db.execute(
            select(Flight.url).where(Flight.is_active == True)
        )
        hotel_result = await db.execute(
            select(Hotel.url).where(Hotel.is_active == True)
        )
        urls = [row[0] for row in flight_result.all()] + [row[0] for row in hotel_result.all()]
    
    if not urls:
        return {"status": "no_travel_deals", "count": 0}
    
    batch_size = 20
    batches = [urls[i:i + batch_size] for i in range(0, len(urls), batch_size)]
    
    job = group(scrape_travel_batch.s(batch) for batch in batches)
    result = job.apply_async()
    
    return {
        "status": "distributed",
        "total_urls": len(urls),
        "batches": len(batches),
        "task_id": result.id
    }


async def _distribute_real_estate_scraping():
    """Distribute real estate scraping to multiple workers."""
    from app.real_estate.models.property import Property
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Property.url).where(Property.is_active == True)
        )
        urls = [row[0] for row in result.all()]
    
    if not urls:
        return {"status": "no_properties", "count": 0}
    
    batch_size = 20
    batches = [urls[i:i + batch_size] for i in range(0, len(urls), batch_size)]
    
    job = group(scrape_real_estate_batch.s(batch) for batch in batches)
    result = job.apply_async()
    
    return {
        "status": "distributed",
        "total_urls": len(urls),
        "batches": len(batches),
        "task_id": result.id
    }


async def _distribute_utilities_scraping():
    """Distribute utilities scraping to multiple workers."""
    from app.utilities.models.service import UtilityService
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(UtilityService.url).where(UtilityService.is_active == True)
        )
        urls = [row[0] for row in result.all()]
    
    if not urls:
        return {"status": "no_services", "count": 0}
    
    batch_size = 20
    batches = [urls[i:i + batch_size] for i in range(0, len(urls), batch_size)]
    
    job = group(scrape_utilities_batch.s(batch) for batch in batches)
    result = job.apply_async()
    
    return {
        "status": "distributed",
        "total_urls": len(urls),
        "batches": len(batches),
        "task_id": result.id
    }
