"""Centralized scraper manager for coordinating scraping operations."""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

from loguru import logger
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.scraping.scraper_factory import scraper_factory
from app.ecommerce.models.product import Product as EcommerceProduct
from app.travel.models.flight import Flight
from app.travel.models.hotel import Hotel
from app.travel.models.price_history import TravelPriceHistory
from app.real_estate.models.property import Property
from app.utilities.models.service import UtilityService


class ScraperManager:
    """Centralized manager for all scraping operations."""

    def __init__(self, max_concurrent: int = 5):
        """Initialize scraper manager."""
        self.max_concurrent = max_concurrent
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

    async def scrape_multiple(self, urls: List[str], category: str = "auto") -> List[Dict[str, Any]]:
        """Scrape multiple URLs concurrently."""
        tasks = [self.scrape_url(url, category) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None results and exceptions
        valid_results = []
        for result in results:
            if isinstance(result, dict):
                valid_results.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Scraping task failed: {result}")
                
        return valid_results

    async def scrape_ecommerce_products(self, db: Session) -> int:
        """Scrape all tracked e-commerce products."""
        products = db.query(EcommerceProduct).filter(EcommerceProduct.is_active == True).all()
        urls = [product.url for product in products]
        
        logger.info(f"Scraping {len(urls)} e-commerce products")
        results = await self.scrape_multiple(urls, "ecommerce")
        
        updated_count = 0
        for result in results:
            if result:
                updated_count += await self._update_ecommerce_product(db, result)
                
        db.commit()
        logger.info(f"Updated {updated_count} e-commerce products")
        return updated_count

    async def scrape_travel_deals(self, db: Session) -> int:
        """Scrape all tracked travel deals."""
        # Scrape flights
        flights = db.query(Flight).filter(Flight.is_active == True).all()
        flight_urls = [flight.url for flight in flights if flight.url]
        
        # Scrape hotels
        hotels = db.query(Hotel).filter(Hotel.is_active == True).all()
        hotel_urls = [hotel.url for hotel in hotels if hotel.url]
        
        all_urls = flight_urls + hotel_urls
        logger.info(f"Scraping {len(all_urls)} travel deals")
        
        results = await self.scrape_multiple(all_urls, "travel")
        
        updated_count = 0
        for result in results:
            if result:
                updated_count += await self._update_travel_deal(db, result)
                
        db.commit()
        logger.info(f"Updated {updated_count} travel deals")
        return updated_count

    async def scrape_real_estate_properties(self, db: Session) -> int:
        """Scrape all tracked real estate properties."""
        properties = db.query(Property).filter(Property.is_active == True).all()
        urls = [prop.url for prop in properties if prop.url]
        
        logger.info(f"Scraping {len(urls)} real estate properties")
        results = await self.scrape_multiple(urls, "real_estate")
        
        updated_count = 0
        for result in results:
            if result:
                updated_count += await self._update_property(db, result)
                
        db.commit()
        logger.info(f"Updated {updated_count} properties")
        return updated_count

    async def scrape_utility_services(self, db: Session) -> int:
        """Scrape all tracked utility services."""
        services = db.query(UtilityService).filter(UtilityService.is_active == True).all()
        urls = [service.url for service in services if service.url]
        
        logger.info(f"Scraping {len(urls)} utility services")
        results = await self.scrape_multiple(urls, "utilities")
        
        updated_count = 0
        for result in results:
            if result:
                updated_count += await self._update_utility_service(db, result)
                
        db.commit()
        logger.info(f"Updated {updated_count} utility services")
        return updated_count

    async def scrape_all_categories(self, db: Session) -> Dict[str, int]:
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

    async def _update_ecommerce_product(self, db: Session, data: Dict[str, Any]) -> int:
        """Update e-commerce product with scraped data."""
        try:
            product = db.query(EcommerceProduct).filter(
                EcommerceProduct.url == data["url"]
            ).first()
            
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

    async def _update_travel_deal(self, db: Session, data: Dict[str, Any]) -> int:
        """Update travel deal with scraped data and record price history."""
        try:
            # Try to find flight first
            flight = db.query(Flight).filter(Flight.url == data["url"]).first()
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
                        source="scraper"
                    )
                    db.add(price_history)
                return 1
                
            # Try to find hotel
            hotel = db.query(Hotel).filter(Hotel.url == data["url"]).first()
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
                        source="scraper"
                    )
                    db.add(price_history)
                return 1
                
            return 0
            
        except Exception as e:
            logger.error(f"Failed to update travel deal: {e}")
            return 0

    async def _update_property(self, db: Session, data: Dict[str, Any]) -> int:
        """Update property with scraped data."""
        try:
            property_obj = db.query(Property).filter(Property.url == data["url"]).first()
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

    async def _update_utility_service(self, db: Session, data: Dict[str, Any]) -> int:
        """Update utility service with scraped data."""
        try:
            service = db.query(UtilityService).filter(
                UtilityService.url == data["url"]
            ).first()
            
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


# Global manager instance
scraper_manager = ScraperManager()