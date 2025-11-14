"""Centralized scraper manager for coordinating scraping operations."""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.scraping.scraper_factory import scraper_factory
from app.ecommerce.models.product import Product as EcommerceProduct
from app.real_estate.models.property import Property
from app.travel.models.flight import Flight
from app.travel.models.hotel import Hotel
from app.travel.models.price_history import TravelPriceHistory
from app.utilities.models.service import UtilityService


class ScraperManager:
    """Centralized manager for all scraping operations."""

    def __init__(self, max_concurrent: int = 10, batch_size: int = 50):
        """Initialize scraper manager with concurrency and batching."""
        self.max_concurrent = max_concurrent
        self.batch_size = batch_size
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def scrape_url(self, url: str, category: str = "auto") -> Optional[Dict[str, Any]]:
        """Scrape single URL with appropriate scraper."""
        async with self.semaphore:
            try:
                scraper = scraper_factory.get_scraper(url, category)
                if not scraper:
                    logger.error(f"No scraper available for {url}")
                    return None

                async with scraper:
                    return await scraper.scrape(url)

            except Exception as e:
                logger.error(f"Failed to scrape {url}: {e}")
                return None

    async def scrape_multiple(
        self, urls: List[str], category: str = "auto"
    ) -> List[Dict[str, Any]]:
        """Scrape multiple URLs concurrently with batching."""
        if not urls:
            return []
        
        all_results = []
        
        # Process in batches to avoid overwhelming memory
        for i in range(0, len(urls), self.batch_size):
            batch = urls[i:i + self.batch_size]
            logger.info(f"Processing batch {i//self.batch_size + 1}: {len(batch)} URLs")
            
            tasks = [self.scrape_url(url, category) for url in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out None results and exceptions
            for result in results:
                if isinstance(result, dict):
                    all_results.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"Scraping task failed: {result}")
            
            # Small delay between batches
            if i + self.batch_size < len(urls):
                await asyncio.sleep(2)
        
        return all_results

    async def scrape_ecommerce_products(self, db: AsyncSession) -> int:
        """Scrape all tracked e-commerce products concurrently."""
        result = await db.execute(
            select(EcommerceProduct).where(EcommerceProduct.is_active == True)
        )
        products = result.scalars().all()
        
        if not products:
            logger.info("No e-commerce products to scrape")
            return 0
        
        urls = [product.url for product in products]
        logger.info(f"Scraping {len(urls)} e-commerce products with {self.max_concurrent} concurrent workers")
        
        results = await self.scrape_multiple(urls, "ecommerce")
        logger.info(f"Successfully scraped {len(results)}/{len(urls)} products")

        updated_count = 0
        for result in results:
            if result:
                updated_count += await self._update_ecommerce_product(db, result)
        
        # Batch commit for better performance
        await db.commit()
        logger.info(f"Updated {updated_count} e-commerce products in database")
        return updated_count

    async def scrape_travel_deals(self, db: AsyncSession) -> int:
        """Scrape all tracked travel deals."""
        # Scrape flights
        result = await db.execute(select(Flight).where(Flight.is_active == True))
        flights = result.scalars().all()
        flight_urls = [flight.url for flight in flights if flight.url]

        # Scrape hotels
        result = await db.execute(select(Hotel).where(Hotel.is_active == True))
        hotels = result.scalars().all()
        hotel_urls = [hotel.url for hotel in hotels if hotel.url]

        all_urls = flight_urls + hotel_urls
        logger.info(f"Scraping {len(all_urls)} travel deals")

        results = await self.scrape_multiple(all_urls, "travel")

        updated_count = 0
        for result in results:
            if result:
                updated_count += await self._update_travel_deal(db, result)

        await db.commit()
        logger.info(f"Updated {updated_count} travel deals")
        return updated_count

    async def scrape_real_estate_properties(self, db: AsyncSession) -> int:
        """Scrape all tracked real estate properties."""
        result = await db.execute(select(Property).where(Property.is_active == True))
        properties = result.scalars().all()
        urls = [prop.url for prop in properties if prop.url]

        logger.info(f"Scraping {len(urls)} real estate properties")
        results = await self.scrape_multiple(urls, "real_estate")

        updated_count = 0
        for result in results:
            if result:
                updated_count += await self._update_property(db, result)

        await db.commit()
        logger.info(f"Updated {updated_count} properties")
        return updated_count

    async def scrape_utility_services(self, db: AsyncSession) -> int:
        """Scrape all tracked utility services."""
        result = await db.execute(select(UtilityService).where(UtilityService.is_active == True))
        services = result.scalars().all()
        urls = [service.url for service in services if service.url]

        logger.info(f"Scraping {len(urls)} utility services")
        results = await self.scrape_multiple(urls, "utilities")

        updated_count = 0
        for result in results:
            if result:
                updated_count += await self._update_utility_service(db, result)

        await db.commit()
        logger.info(f"Updated {updated_count} utility services")
        return updated_count

    async def scrape_all_categories(self, db: AsyncSession) -> Dict[str, int]:
        """Scrape all categories and return update counts."""
        logger.info("Starting comprehensive scraping of all categories")

        results = {}
        try:
            results["ecommerce"] = await self.scrape_ecommerce_products(db)
            results["travel"] = await self.scrape_travel_deals(db)
            results["real_estate"] = await self.scrape_real_estate_properties(db)
            results["utilities"] = await self.scrape_utility_services(db)

            total_updated = sum(results.values())
            logger.info(f"Scraping completed. Total items updated: {total_updated}")

        except Exception as e:
            logger.error(f"Error during comprehensive scraping: {e}")

        return results

    async def _update_ecommerce_product(self, db: AsyncSession, data: Dict[str, Any]) -> int:
        """Update e-commerce product with scraped data."""
        try:
            result = await db.execute(
                select(EcommerceProduct).where(EcommerceProduct.url == data["url"])
            )
            product = result.scalar_one_or_none()

            if not product:
                return 0

            # Update product data
            if data.get("name"):
                product.name = data["name"]
            if data.get("price"):
                product.current_price = data["price"]
            if data.get("availability"):
                product.availability = data["availability"]

            product.last_scraped = datetime.utcnow()
            return 1

        except Exception as e:
            logger.error(f"Failed to update e-commerce product: {e}")
            return 0

    async def _update_travel_deal(self, db: AsyncSession, data: Dict[str, Any]) -> int:
        """Update travel deal with scraped data and record price history."""
        try:
            # Try to find flight first
            result = await db.execute(select(Flight).where(Flight.url == data["url"]))
            flight = result.scalar_one_or_none()
            if flight:
                old_price = flight.price
                if data.get("price") and data["price"] != old_price:
                    flight.price = data["price"]
                    flight.last_updated = datetime.utcnow()

                    # Record price history
                    price_history = TravelPriceHistory(
                        flight_id=flight.id,
                        price=data["price"],
                        currency=data.get("currency", "NGN"),
                        source="scraper",
                    )
                    db.add(price_history)
                return 1

            # Try to find hotel
            result = await db.execute(select(Hotel).where(Hotel.url == data["url"]))
            hotel = result.scalar_one_or_none()
            if hotel:
                old_price = hotel.price_per_night
                if data.get("price") and data["price"] != old_price:
                    hotel.price_per_night = data["price"]
                    hotel.last_updated = datetime.utcnow()

                    # Record price history
                    price_history = TravelPriceHistory(
                        hotel_id=hotel.id,
                        price=data["price"],
                        currency=data.get("currency", "NGN"),
                        source="scraper",
                    )
                    db.add(price_history)
                return 1

            return 0

        except Exception as e:
            logger.error(f"Failed to update travel deal: {e}")
            return 0

    async def _update_property(self, db: AsyncSession, data: Dict[str, Any]) -> int:
        """Update property with scraped data."""
        try:
            result = await db.execute(select(Property).where(Property.url == data["url"]))
            property_obj = result.scalar_one_or_none()
            if not property_obj:
                return 0

            if data.get("price"):
                property_obj.price = data["price"]
            if data.get("name"):
                property_obj.title = data["name"]

            property_obj.last_updated = datetime.utcnow()
            return 1

        except Exception as e:
            logger.error(f"Failed to update property: {e}")
            return 0

    async def _update_utility_service(self, db: AsyncSession, data: Dict[str, Any]) -> int:
        """Update utility service with scraped data."""
        try:
            result = await db.execute(select(UtilityService).where(UtilityService.url == data["url"]))
            service = result.scalar_one_or_none()

            if not service:
                return 0

            if data.get("price"):
                service.price = data["price"]
            if data.get("name"):
                service.name = data["name"]

            service.last_updated = datetime.utcnow()
            return 1

        except Exception as e:
            logger.error(f"Failed to update utility service: {e}")
            return 0


# Global manager instance with configurable settings
from app.core.config import settings

scraper_manager = ScraperManager(
    max_concurrent=settings.scraper_max_concurrent,
    batch_size=settings.scraper_batch_size
)
