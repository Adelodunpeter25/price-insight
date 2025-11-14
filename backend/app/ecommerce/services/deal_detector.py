"""E-commerce deal detection service."""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.deal_detection.base_detector import BaseDealDetector
from app.core.services.notification_service import NotificationService
from app.core.tasks.email_tasks import send_deal_notification_task
from app.core.models.user import User
from app.ecommerce.services.price_analytics import PriceAnalytics

logger = logging.getLogger(__name__)
from app.ecommerce.models.deal import Deal
from app.ecommerce.models.deal_preference import DealPreference
from app.ecommerce.models.price_history import PriceHistory
from app.ecommerce.models.product import Product


class EcommerceDealDetector(BaseDealDetector):
    """Deal detector for e-commerce products."""

    async def get_items_for_detection(self, db: Session) -> List[Product]:
        """Get active products for deal detection."""
        return (
            db.query(Product)
            .filter(Product.is_active, Product.current_price.isnot(None))
            .all()
        )

    def get_price_history(self, db: Session, item: Product) -> List[PriceHistory]:
        """Get price history for product."""
        return (
            db.query(PriceHistory)
            .filter(PriceHistory.product_id == item.id)
            .order_by(PriceHistory.recorded_at.desc())
            .limit(30)
            .all()
        )

    def get_current_price(self, item: Product) -> Optional[Decimal]:
        """Get current price from product."""
        return item.current_price

    async def create_deal(self, db: Session, item: Product, deal_data: Dict) -> Optional[Deal]:
        """Create e-commerce deal record with enhanced analytics."""
        try:
            # Get price analytics for better deal description
            stats = PriceAnalytics.get_price_stats(db, item.id, 30)
            trend = PriceAnalytics.get_price_trend(db, item.id, 7)
            
            # Check if deal already exists for this product
            existing_deal = (
                db.query(Deal).filter(Deal.product_id == item.id, Deal.is_active).first()
            )

            if existing_deal:
                # Update existing deal
                existing_deal.discount_percent = deal_data["discount_percent"]
                existing_deal.original_price = deal_data["original_price"]
                existing_deal.deal_price = deal_data["current_price"]
                existing_deal.savings = deal_data["savings"]
                existing_deal.updated_at = datetime.utcnow()
                return existing_deal
            else:
                # Enhanced description with analytics
                description = f"{deal_data['discount_percent']:.1f}% off - Save ₦{deal_data['savings']:.2f}"
                if stats:
                    if stats['current_price'] == stats['lowest_price']:
                        description += " | Lowest price in 30 days!"
                    elif trend == "falling":
                        description += " | Price trending down"
                
                # Create new deal
                deal = Deal(
                    product_id=item.id,
                    title=f"Deal: {item.name}",
                    description=description,
                    original_price=deal_data["original_price"],
                    deal_price=deal_data["current_price"],
                    discount_percent=deal_data["discount_percent"],
                    savings=deal_data["savings"],
                    is_active=True,
                    created_at=datetime.utcnow(),
                )
                db.add(deal)
                db.flush()
                
                # Send email notification
                await self._send_deal_notification(db, item, deal_data, stats)
                
                return deal

        except Exception as e:
            logger.error(f"Failed to create e-commerce deal: {e}")
            return None

    async def _send_deal_notification(self, db: Session, product: Product, deal_data: Dict, stats: Optional[Dict] = None) -> None:
        """Send notifications to users with matching deal preferences."""
        try:
            # Get users with deal preferences for this product
            preferences = db.query(DealPreference).filter(
                DealPreference.product_id == product.id,
                DealPreference.enable_deal_alerts == True
            ).all()
            
            notification_service = NotificationService(db)
            discount_percent = float(deal_data["discount_percent"])
            current_price = float(deal_data["current_price"])
            
            # Add analytics context to notification
            extra_info = ""
            if stats:
                if stats['current_price'] == stats['lowest_price']:
                    extra_info = " This is the lowest price in 30 days!"
                elif stats['savings_percentage'] > 15:
                    extra_info = f" You're saving {stats['savings_percentage']:.1f}% vs average price!"
            
            for preference in preferences:
                # Check if deal meets user's criteria
                if not self._meets_deal_criteria(preference, discount_percent, current_price):
                    continue
                    
                user = preference.user
                
                # Send email via Celery (non-blocking with retry)
                send_deal_notification_task.delay(
                    to=user.email,
                    item_name=product.name + extra_info,
                    category="E-commerce",
                    price=current_price,
                    provider=product.site,
                    discount_percent=discount_percent,
                    currency="₦"
                )
                
                # Send in-app notification
                notification_service.notify_deal_alert(
                    user_id=user.id,
                    product_name=product.name,
                    discount_percent=discount_percent
                )
                
        except Exception as e:
            logger.error(f"Failed to send deal notification: {e}")
    
    def _meets_deal_criteria(self, preference: DealPreference, discount_percent: float, current_price: float) -> bool:
        """Check if deal meets user's criteria."""
        # Check minimum discount
        if discount_percent < float(preference.min_discount_percent):
            return False
            
        # Check price threshold
        if preference.max_price_threshold and current_price > float(preference.max_price_threshold):
            return False
            
        # Check deal types (simplified - just check if percentage deals are enabled)
        deal_types = preference.get_deal_types()
        if "percentage" not in deal_types:
            return False
            
        return True
