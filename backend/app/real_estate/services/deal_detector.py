"""Real estate deal detection service."""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.deal_detection.base_detector import BaseDealDetector
from app.real_estate.models.deal import PropertyDeal
from app.real_estate.models.price_history import PropertyPriceHistory
from app.real_estate.models.property import Property
from app.real_estate.services.price_analytics import PropertyPriceAnalytics

logger = logging.getLogger(__name__)


class RealEstateDealDetector(BaseDealDetector):
    """Deal detector for real estate properties."""

    def get_items_for_detection(self, db: Session) -> List[Property]:
        """Get active properties for deal detection."""
        return (
            db.query(Property).filter(Property.is_active, Property.price.isnot(None)).all()
        )

    def get_price_history(self, db: Session, item: Property) -> List[PropertyPriceHistory]:
        """Get price history for property."""
        return (
            db.query(PropertyPriceHistory)
            .filter(PropertyPriceHistory.property_id == item.id)
            .order_by(PropertyPriceHistory.created_at.desc())
            .limit(30)
            .all()
        )

    def get_current_price(self, item: Property) -> Optional[Decimal]:
        """Get current price from property."""
        return item.price

    def create_deal(self, db: Session, item: Property, deal_data: Dict) -> Optional[PropertyDeal]:
        """Create real estate deal record with analytics."""
        try:
            stats = PropertyPriceAnalytics.get_price_stats(db, item.id, 30)
            trend = PropertyPriceAnalytics.get_price_trend(db, item.id, 7)

            description = f"{deal_data['discount_percent']:.1f}% price reduction - Save ₦{deal_data['savings']:.2f}"

            if stats and stats['current_price'] == stats['lowest_price']:
                description += " | Lowest price in 30 days!"
            elif trend == "falling":
                description += " | Price trending down"

            existing_deal = (
                db.query(PropertyDeal)
                .filter(PropertyDeal.property_id == item.id, PropertyDeal.is_active == True)
                .first()
            )

            if existing_deal:
                existing_deal.discount_percent = deal_data["discount_percent"]
                existing_deal.original_price = deal_data["original_price"]
                existing_deal.deal_price = deal_data["current_price"]
                existing_deal.description = description
                existing_deal.updated_at = datetime.utcnow()
                return existing_deal
            else:
                deal = PropertyDeal(
                    property_id=item.id,
                    deal_type="price_drop",
                    description=description,
                    original_price=deal_data["original_price"],
                    deal_price=deal_data["current_price"],
                    discount_percent=deal_data["discount_percent"],
                )
                db.add(deal)
                db.flush()
                return deal

        except Exception as e:
            logger.error(f"Failed to create property deal: {e}")
            return None
