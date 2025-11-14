"""Utilities deal detection service."""

from decimal import Decimal
from typing import List, Dict, Any, Optional
from datetime import datetime

from sqlalchemy.orm import Session
from loguru import logger

from app.core.deal_detection.base_detector import BaseDealDetector
from app.utilities.models.service import UtilityService
from app.utilities.models.price_history import PriceHistory
from app.utilities.models.deal import UtilityDeal


class UtilityDealDetector(BaseDealDetector):
    """Deal detector for utility services."""

    def get_items_for_detection(self, db: Session) -> List[UtilityService]:
        """Get active utility services for deal detection."""
        return db.query(UtilityService).filter(
            UtilityService.is_active == True,
            UtilityService.price.isnot(None)
        ).all()

    def get_price_history(self, db: Session, item: UtilityService) -> List[PriceHistory]:
        """Get price history for utility service."""
        return db.query(PriceHistory).filter(
            PriceHistory.service_id == item.id
        ).order_by(PriceHistory.recorded_at.desc()).limit(30).all()

    def get_current_price(self, item: UtilityService) -> Optional[Decimal]:
        """Get current price from utility service."""
        return item.price

    def create_deal(self, db: Session, item: UtilityService, deal_data: Dict) -> Optional[UtilityDeal]:
        """Create utility deal record."""
        try:
            # Check if deal already exists
            existing_deal = db.query(UtilityDeal).filter(
                UtilityDeal.service_id == item.id,
                UtilityDeal.is_active == True
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
                deal = UtilityDeal(
                    service_id=item.id,
                    title=f"Service Deal: {item.name}",
                    description=f"{deal_data['discount_percent']:.1f}% discount - Save ₦{deal_data['savings']:.2f}",
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
            logger.error(f"Failed to create utility deal: {e}")
            return None