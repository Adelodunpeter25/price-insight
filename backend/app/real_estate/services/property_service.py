"""Property service for database operations."""

import json
from decimal import Decimal
from typing import List, Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.real_estate.models import Property, PropertyPriceHistory


class PropertyService:
    """Service for property database operations."""

    def __init__(self, db: AsyncSession):
        """Initialize service."""
        self.db = db

    async def get_or_create_property(
        self,
        url: str,
        name: str,
        property_type: str,
        location: str,
        site: str,
        listing_type: str = "sale",
        bedrooms: Optional[int] = None,
        bathrooms: Optional[int] = None,
        size_sqm: Optional[Decimal] = None,
        features: Optional[List[str]] = None,
    ) -> Property:
        """Get existing property or create new one."""

        # Check if property exists
        query = select(Property).where(Property.url == url, Property.is_active)
        result = await self.db.execute(query)
        existing_property = result.scalar_one_or_none()

        if existing_property:
            logger.info(f"Property already exists: {existing_property.name}")
            return existing_property

        # Create new property
        property_data = {
            "name": name,
            "property_type": property_type,
            "location": location,
            "url": url,
            "site": site,
            "listing_type": listing_type,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "size_sqm": size_sqm,
            "price": Decimal("0"),  # Will be updated by scraper
            "currency": "NGN",
            "is_tracked": 1,
        }

        if features:
            property_data["features"] = json.dumps(features)

        new_property = Property(**property_data)
        self.db.add(new_property)
        await self.db.commit()
        await self.db.refresh(new_property)

        logger.info(f"Created new property: {new_property.name}")
        return new_property

    async def add_price_history(
        self,
        property_id: int,
        price: Decimal,
        currency: str = "NGN",
        price_per_sqm: Optional[Decimal] = None,
        listing_status: Optional[str] = None,
    ) -> PropertyPriceHistory:
        """Add price history entry."""

        price_history = PropertyPriceHistory(
            property_id=property_id,
            price=price,
            currency=currency,
            price_per_sqm=price_per_sqm,
            listing_status=listing_status,
        )

        self.db.add(price_history)

        # Update current price in property
        query = select(Property).where(Property.id == property_id)
        result = await self.db.execute(query)
        property_obj = result.scalar_one_or_none()

        if property_obj:
            property_obj.price = price
            property_obj.currency = currency
            if price_per_sqm:
                property_obj.price_per_sqm = price_per_sqm

        await self.db.commit()
        await self.db.refresh(price_history)

        logger.info(f"Added price history for property {property_id}: ₦{price}")
        return price_history

    async def get_latest_price(self, property_id: int) -> Optional[PropertyPriceHistory]:
        """Get latest price history entry."""

        query = (
            select(PropertyPriceHistory)
            .where(PropertyPriceHistory.property_id == property_id)
            .order_by(PropertyPriceHistory.created_at.desc())
            .limit(1)
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_properties_to_track(self) -> List[Property]:
        """Get all properties that should be tracked."""

        query = select(Property).where(Property.is_tracked == 1, Property.is_active)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_property_with_history(self, property_id: int) -> Optional[Property]:
        """Get property with price history."""

        query = (
            select(Property)
            .options(selectinload(Property.price_history))
            .where(Property.id == property_id, Property.is_active)
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()
