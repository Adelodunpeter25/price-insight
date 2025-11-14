"""E-commerce deal detection service."""

from decimal import Decimal
from typing import List, Dict, Any, Optional
from datetime import datetime

from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

from app.core.deal_detection.base_detector import BaseDealDetector
from app.ecommerce.models.product import Product
from app.ecommerce.models.price_history import PriceHistory
from app.ecommerce.models.deal import Deal


class EcommerceDealDetector(BaseDealDetector):
    """Deal detector for e-commerce products."""

    def get_items_for_detection(self, db: Session) -> List[Product]:
        """Get active products for deal detection."""
        return db.query(Product).filter(
            Product.is_active == True,
            Product.current_price.isnot(None)
        ).all()

    def get_price_history(self, db: Session, item: Product) -> List[PriceHistory]:
        """Get price history for product."""
        return db.query(PriceHistory).filter(
            PriceHistory.product_id == item.id
        ).order_by(PriceHistory.recorded_at.desc()).limit(30).all()

    def get_current_price(self, item: Product) -> Optional[Decimal]:
        """Get current price from product."""
        return item.current_price

    def create_deal(self, db: Session, item: Product, deal_data: Dict) -> Optional[Deal]:
        """Create e-commerce deal record."""
        try:
            # Check if deal already exists for this product
            existing_deal = db.query(Deal).filter(
                Deal.product_id == item.id,
                Deal.is_active == True
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
                deal = Deal(
                    product_id=item.id,
                    title=f"Deal: {item.name}",
                    description=f"{deal_data['discount_percent']:.1f}% off - Save ₦{deal_data['savings']:.2f}",
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
            logger.error(f"Failed to create e-commerce deal: {e}")
            return None