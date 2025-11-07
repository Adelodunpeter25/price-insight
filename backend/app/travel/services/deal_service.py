"""Travel deal service."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.travel.models.deal import TravelDeal


class TravelDealService:
    """Service for travel deal operations."""

    def __init__(self, db: AsyncSession):
        """Initialize service."""
        self.db = db

    async def create_deal(
        self,
        flight_id: Optional[int] = None,
        hotel_id: Optional[int] = None,
        discount_percent: Optional[float] = None,
        original_price: Optional[float] = None,
        deal_price: float = 0.0,
        deal_start_date: Optional[datetime] = None,
        deal_end_date: Optional[datetime] = None,
        deal_source: str = "manual",
        deal_description: Optional[str] = None,
    ) -> TravelDeal:
        """Create new travel deal."""
        deal = TravelDeal(
            flight_id=flight_id,
            hotel_id=hotel_id,
            discount_percent=discount_percent,
            original_price=original_price,
            deal_price=deal_price,
            deal_start_date=deal_start_date,
            deal_end_date=deal_end_date,
            deal_source=deal_source,
            deal_description=deal_description,
        )
        self.db.add(deal)
        await self.db.commit()
        await self.db.refresh(deal)
        return deal

    async def get_active_deals(self) -> List[TravelDeal]:
        """Get all active travel deals."""
        query = select(TravelDeal).where(
            TravelDeal.is_active, TravelDeal.deal_end_date > datetime.utcnow()
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_deal_by_id(self, deal_id: int) -> Optional[TravelDeal]:
        """Get deal by ID."""
        query = select(TravelDeal).where(TravelDeal.id == deal_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
