"""Travel price scraping job."""

import logging
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_database_session
from app.travel.models import Flight, Hotel
from app.travel.services.scrapers.flight_scraper import FlightScraper
from app.travel.services.scrapers.hotel_scraper import HotelScraper

logger = logging.getLogger(__name__)


async def scrape_travel_prices():
    """Scrape travel prices for tracked flights and hotels."""
    async for db in get_database_session():
        try:
            await _scrape_flights(db)
            await _scrape_hotels(db)
        except Exception as e:
            logger.error(f"Travel scraping job failed: {e}")
        finally:
            await db.close()


async def _scrape_flights(db: AsyncSession):
    """Scrape flight prices."""
    from app.travel.services.travel_alert_service import TravelAlertService
    
    query = select(Flight).where(Flight.is_tracked == True, Flight.is_active == True)
    result = await db.execute(query)
    flights = result.scalars().all()
    
    scraper = FlightScraper()
    alert_service = TravelAlertService(db)
    
    for flight in flights:
        try:
            data = await scraper.scrape(flight.url)
            if data and "price" in data:
                old_price = flight.price
                new_price = Decimal(str(data["price"]))
                flight.price = new_price
                
                if data.get("airline"):
                    flight.airline = data["airline"]
                
                await db.commit()
                logger.info(f"Updated flight {flight.id}: {old_price} -> {new_price}")
                
                # Check alerts
                await alert_service.check_flight_alerts(flight, old_price, new_price)
                
        except Exception as e:
            logger.error(f"Failed to scrape flight {flight.id}: {e}")


async def _scrape_hotels(db: AsyncSession):
    """Scrape hotel prices."""
    from app.travel.services.travel_alert_service import TravelAlertService
    
    query = select(Hotel).where(Hotel.is_tracked == True, Hotel.is_active == True)
    result = await db.execute(query)
    hotels = result.scalars().all()
    
    scraper = HotelScraper()
    alert_service = TravelAlertService(db)
    
    for hotel in hotels:
        try:
            data = await scraper.scrape(hotel.url)
            if data and "price_per_night" in data:
                old_price = hotel.price_per_night
                new_price = Decimal(str(data["price_per_night"]))
                hotel.price_per_night = new_price
                hotel.total_price = Decimal(str(data.get("total_price", new_price)))
                
                if data.get("rating"):
                    hotel.rating = Decimal(str(data["rating"]))
                
                await db.commit()
                logger.info(f"Updated hotel {hotel.id}: {old_price} -> {new_price}")
                
                # Check alerts
                await alert_service.check_hotel_alerts(hotel, old_price, new_price)
                
        except Exception as e:
            logger.error(f"Failed to scrape hotel {hotel.id}: {e}")