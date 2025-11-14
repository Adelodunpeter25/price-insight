"""Base deal detection engine."""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from loguru import logger
from sqlalchemy.orm import Session

from app.utils.helpers import calculate_discount_percentage, is_valid_deal


class BaseDealDetector(ABC):
    """Base class for deal detection across categories."""

    def __init__(self, min_discount: Decimal = Decimal("10")):
        """Initialize detector with minimum discount threshold."""
        self.min_discount = min_discount

    @abstractmethod
    def get_items_for_detection(self, db: Session) -> List[Any]:
        """Get items to check for deals. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def get_price_history(self, db: Session, item: Any) -> List[Any]:
        """Get price history for item. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def create_deal(self, db: Session, item: Any, deal_data: Dict) -> Any:
        """Create deal record. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def get_current_price(self, item: Any) -> Optional[Decimal]:
        """Get current price from item. Must be implemented by subclasses."""
        pass

    def detect_price_drop(self, current_price: Decimal, price_history: List[Any]) -> Optional[Dict]:
        """Detect if current price represents a significant drop."""
        if not price_history:
            return None

        # Get recent prices (last 7 days)
        recent_cutoff = datetime.utcnow() - timedelta(days=7)
        recent_prices = [
            p for p in price_history 
            if hasattr(p, 'recorded_at') and p.recorded_at >= recent_cutoff
        ]

        if not recent_prices:
            return None

        # Find highest recent price
        highest_price = max(
            getattr(p, 'price', Decimal('0')) for p in recent_prices
        )

        if highest_price <= current_price:
            return None

        # Calculate discount
        discount_percent = calculate_discount_percentage(highest_price, current_price)
        
        if is_valid_deal(discount_percent, self.min_discount):
            return {
                "original_price": highest_price,
                "current_price": current_price,
                "discount_percent": discount_percent,
                "savings": highest_price - current_price
            }

        return None

    def detect_deals(self, db: Session) -> List[Dict]:
        """Main deal detection method."""
        items = self.get_items_for_detection(db)
        detected_deals = []

        for item in items:
            try:
                current_price = self.get_current_price(item)
                if not current_price:
                    continue

                price_history = self.get_price_history(db, item)
                deal_data = self.detect_price_drop(current_price, price_history)

                if deal_data:
                    # Create deal record
                    deal = self.create_deal(db, item, deal_data)
                    if deal:
                        detected_deals.append({
                            "item": item,
                            "deal": deal,
                            "deal_data": deal_data
                        })
                        logger.info(f"Deal detected: {deal_data['discount_percent']:.1f}% off")

            except Exception as e:
                logger.error(f"Error detecting deals for item {getattr(item, 'id', 'unknown')}: {e}")

        return detected_deals