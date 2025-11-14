"""Real estate deal detection service."""

from decimal import Decimal
from typing import List, Dict, Any, Optional
from datetime import datetime

from sqlalchemy.orm import Session
from loguru import logger

from app.core.deal_detection.base_detector import BaseDealDetector
from app.real_estate.models.property import Property
from app.real_estate.models.price_history import PriceHistory
from app.real_estate.models.deal import RealEstateDeal


class RealEstateDealDetector(BaseDealDetector):
    """Deal detector for real estate properties."""

    def get_items_for_detection(self, db: Session) -> List[Property]:
        """Get active properties for deal detection."""
        return db.query(Property).filter(
            Property.is_active == True,
            Property.price.isnot(None)
        ).all()

    def get_price_history(self, db: Session, item: Property) -> List[PriceHistory]:
        """Get price history for property."""
        return db.query(PriceHistory).filter(
            PriceHistory.property_id == item.id
        ).order_by(PriceHistory.recorded_at.desc()).limit(30).all()

    def get_current_price(self, item: Property) -> Optional[Decimal]:
        """Get current price from property."""
        return item.price

    def create_deal(self, db: Session, item: Property, deal_data: Dict) -> Optional[RealEstateDeal]:
        """Create real estate deal record."""
        try:
            # Check if deal already exists
            existing_deal = db.query(RealEstateDeal).filter(
                RealEstateDeal.property_id == item.id,
                RealEstateDeal.is_active == True
            ).first()

            if existing_deal:
                # Update existing deal
                existing_deal.discount_percent = deal_data["discount_percent"]
                existing_deal.original_price = deal_data["original_price"]
                existing_deal.deal_price = deal_data["current_price"]
                existing_deal.savings = deal_data["savings"]
                existing_deal.updated_at = datetime.utcnow()
                return existing_deal
            else:
                # Create new deal
                deal = RealEstateDeal(
                    property_id=item.id,
                    title=f"Property Deal: {item.title}",
                    description=f"{deal_data['discount_percent']:.1f}% price reduction - Save ₦{deal_data['savings']:.2f}",
                    original_price=deal_data["original_price"],
                    deal_price=deal_data["current_price"],
                    discount_percent=deal_data["discount_percent"],
                    savings=deal_data["savings"],
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                db.add(deal)
                db.flush()
                return deal

        except Exception as e:
            logger.error(f"Failed to create real estate deal: {e}")
            return None