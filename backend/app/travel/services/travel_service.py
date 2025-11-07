"""Travel service for database operations."""

import logging
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.travel.models import Flight, Hotel

logger = logging.getLogger(__name__)


class TravelService:
    """Service for travel-related database operations."""

    def __init__(self, db: AsyncSession):
        """Initialize service."""
        self.db = db

    async def create_flight(
        self,
        origin: str,
        destination: str,
        departure_date,
        return_date,
        flight_class: str,
        passengers: int,
        url: str,
        site: str,
    ) -> Flight:
        """Create new flight tracking."""
        flight = Flight(
            origin=origin.upper(),
            destination=destination.upper(),
            departure_date=departure_date,
            return_date=return_date,
            flight_class=flight_class,
            passengers=passengers,
            url=str(url),
            site=site,
            price=0.0,  # Will be updated by scraper
            currency="NGN",  # All prices normalized to Naira
        )
        
        self.db.add(flight)
        await self.db.commit()
        await self.db.refresh(flight)
        
        logger.info(f"Created flight tracking: {origin}-{destination}")
        return flight

    async def create_hotel(
        self,
        name: str,
        location: str,
        check_in,
        check_out,
        room_type: str,
        guests: int,
        url: str,
        site: str,
    ) -> Hotel:
        """Create new hotel tracking."""
        hotel = Hotel(
            name=name,
            location=location,
            check_in=check_in,
            check_out=check_out,
            room_type=room_type,
            guests=guests,
            url=str(url),
            site=site,
            price_per_night=0.0,  # Will be updated by scraper
            total_price=0.0,
            currency="NGN",  # All prices normalized to Naira
        )
        
        self.db.add(hotel)
        await self.db.commit()
        await self.db.refresh(hotel)
        
        logger.info(f"Created hotel tracking: {name} in {location}")
        return hotel

    async def get_tracked_flights(self) -> List[Flight]:
        """Get all tracked flights."""
        query = select(Flight).where(Flight.is_tracked == True, Flight.is_active == True)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_tracked_hotels(self) -> List[Hotel]:
        """Get all tracked hotels."""
        query = select(Hotel).where(Hotel.is_tracked == True, Hotel.is_active == True)
        result = await self.db.execute(query)
        return list(result.scalars().all())