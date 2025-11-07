"""Utility service for database operations."""

from decimal import Decimal
from typing import List, Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.utilities.models import UtilityService, UtilityPriceHistory


class UtilityServiceManager:
    """Service for utility database operations."""

    def __init__(self, db: AsyncSession):
        """Initialize service."""
        self.db = db

    async def get_or_create_service(
        self,
        url: str,
        name: str,
        service_type: str,
        provider: str,
        site: str,
        billing_type: str = "subscription",
        billing_cycle: Optional[str] = None,
        plan_details: Optional[str] = None,
    ) -> UtilityService:
        """Get existing service or create new one."""

        # Check if service exists
        query = select(UtilityService).where(UtilityService.url == url, UtilityService.is_active)
        result = await self.db.execute(query)
        existing_service = result.scalar_one_or_none()

        if existing_service:
            logger.info(f"Service already exists: {existing_service.name}")
            return existing_service

        # Create new service
        service_data = {
            "name": name,
            "service_type": service_type,
            "provider": provider,
            "url": url,
            "site": site,
            "billing_type": billing_type,
            "billing_cycle": billing_cycle,
            "plan_details": plan_details,
            "base_price": Decimal("0"),  # Will be updated by scraper
            "currency": "NGN",
            "is_tracked": 1,
        }

        new_service = UtilityService(**service_data)
        self.db.add(new_service)
        await self.db.commit()
        await self.db.refresh(new_service)

        logger.info(f"Created new service: {new_service.name}")
        return new_service

    async def add_price_history(
        self,
        service_id: int,
        price: Decimal,
        currency: str = "NGN",
        tariff_details: Optional[str] = None,
    ) -> UtilityPriceHistory:
        """Add price history entry."""

        price_history = UtilityPriceHistory(
            service_id=service_id,
            price=price,
            currency=currency,
            tariff_details=tariff_details,
        )

        self.db.add(price_history)

        # Update current price in service
        query = select(UtilityService).where(UtilityService.id == service_id)
        result = await self.db.execute(query)
        service_obj = result.scalar_one_or_none()

        if service_obj:
            service_obj.base_price = price
            service_obj.currency = currency

        await self.db.commit()
        await self.db.refresh(price_history)

        logger.info(f"Added price history for service {service_id}: ₦{price}")
        return price_history

    async def get_latest_price(self, service_id: int) -> Optional[UtilityPriceHistory]:
        """Get latest price history entry."""

        query = (
            select(UtilityPriceHistory)
            .where(UtilityPriceHistory.service_id == service_id)
            .order_by(UtilityPriceHistory.created_at.desc())
            .limit(1)
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_services_to_track(self) -> List[UtilityService]:
        """Get all services that should be tracked."""

        query = select(UtilityService).where(
            UtilityService.is_tracked == 1, UtilityService.is_active
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_service_with_history(self, service_id: int) -> Optional[UtilityService]:
        """Get service with price history."""

        query = (
            select(UtilityService)
            .options(selectinload(UtilityService.price_history))
            .where(UtilityService.id == service_id, UtilityService.is_active)
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()
