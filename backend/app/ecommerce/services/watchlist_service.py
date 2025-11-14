"""Watchlist service for managing user product tracking."""

import logging
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.services.email_service import email_service
from app.core.services.notification_service import NotificationService
from app.ecommerce.models.price_history import PriceHistory
from app.ecommerce.models.product import Product
from app.ecommerce.models.watchlist import Watchlist

logger = logging.getLogger(__name__)


class WatchlistService:
    """Service for managing user watchlists."""

    @staticmethod
    def add_to_watchlist(
        db: Session,
        user_id: int,
        product_id: int,
        target_price: Optional[Decimal] = None,
        alert_on_any_drop: bool = True,
        alert_on_target: bool = True,
        notes: Optional[str] = None
    ) -> Optional[Watchlist]:
        """Add product to user's watchlist."""
        try:
            # Check if already in watchlist
            existing = db.query(Watchlist).filter(
                Watchlist.user_id == user_id,
                Watchlist.product_id == product_id
            ).first()
            
            if existing:
                return existing
            
            # Verify product exists
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                return None
            
            watchlist = Watchlist(
                user_id=user_id,
                product_id=product_id,
                target_price=target_price,
                alert_on_any_drop=alert_on_any_drop,
                alert_on_target=alert_on_target,
                notes=notes
            )
            
            db.add(watchlist)
            db.commit()
            db.refresh(watchlist)
            
            logger.info(f"Added product {product_id} to watchlist for user {user_id}")
            return watchlist
            
        except Exception as e:
            logger.error(f"Error adding to watchlist: {e}")
            db.rollback()
            return None

    @staticmethod
    def remove_from_watchlist(db: Session, user_id: int, watchlist_id: int) -> bool:
        """Remove product from user's watchlist."""
        try:
            watchlist = db.query(Watchlist).filter(
                Watchlist.id == watchlist_id,
                Watchlist.user_id == user_id
            ).first()
            
            if not watchlist:
                return False
            
            db.delete(watchlist)
            db.commit()
            
            logger.info(f"Removed watchlist item {watchlist_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing from watchlist: {e}")
            db.rollback()
            return False

    @staticmethod
    def update_watchlist(
        db: Session,
        user_id: int,
        watchlist_id: int,
        target_price: Optional[Decimal] = None,
        alert_on_any_drop: Optional[bool] = None,
        alert_on_target: Optional[bool] = None,
        notes: Optional[str] = None
    ) -> Optional[Watchlist]:
        """Update watchlist item."""
        try:
            watchlist = db.query(Watchlist).filter(
                Watchlist.id == watchlist_id,
                Watchlist.user_id == user_id
            ).first()
            
            if not watchlist:
                return None
            
            if target_price is not None:
                watchlist.target_price = target_price
            if alert_on_any_drop is not None:
                watchlist.alert_on_any_drop = alert_on_any_drop
            if alert_on_target is not None:
                watchlist.alert_on_target = alert_on_target
            if notes is not None:
                watchlist.notes = notes
            
            db.commit()
            db.refresh(watchlist)
            
            return watchlist
            
        except Exception as e:
            logger.error(f"Error updating watchlist: {e}")
            db.rollback()
            return None

    @staticmethod
    def get_user_watchlist(db: Session, user_id: int) -> List[Watchlist]:
        """Get all watchlist items for a user."""
        return db.query(Watchlist).filter(Watchlist.user_id == user_id).all()

    @staticmethod
    async def check_watchlist_alerts(db: Session) -> None:
        """Check all watchlist items for price alerts."""
        try:
            watchlists = db.query(Watchlist).all()
            notification_service = NotificationService(db)
            
            for watchlist in watchlists:
                product = watchlist.product
                
                # Get latest price
                latest_price = db.query(PriceHistory).filter(
                    PriceHistory.product_id == product.id
                ).order_by(PriceHistory.created_at.desc()).first()
                
                if not latest_price:
                    continue
                
                current_price = float(latest_price.price)
                
                # Check target price alert
                if watchlist.alert_on_target and watchlist.target_price:
                    target = float(watchlist.target_price)
                    if current_price <= target:
                        await WatchlistService._send_target_alert(
                            db, watchlist, product, current_price, target
                        )
                
                # Check any price drop alert
                if watchlist.alert_on_any_drop:
                    previous_price = db.query(PriceHistory).filter(
                        PriceHistory.product_id == product.id,
                        PriceHistory.id < latest_price.id
                    ).order_by(PriceHistory.created_at.desc()).first()
                    
                    if previous_price and current_price < float(previous_price.price):
                        drop_pct = ((float(previous_price.price) - current_price) / float(previous_price.price)) * 100
                        await WatchlistService._send_drop_alert(
                            db, watchlist, product, current_price, drop_pct
                        )
                        
        except Exception as e:
            logger.error(f"Error checking watchlist alerts: {e}")

    @staticmethod
    async def _send_target_alert(
        db: Session,
        watchlist: Watchlist,
        product: Product,
        current_price: float,
        target_price: float
    ) -> None:
        """Send alert when target price is reached."""
        try:
            user = watchlist.user
            
            await email_service.send_price_alert(
                to=user.email,
                item_name=product.name,
                category="E-commerce",
                old_price=target_price,
                new_price=current_price,
                provider=product.site,
                currency="₦"
            )
            
            NotificationService(db).notify_price_drop(
                user_id=user.id,
                product_name=product.name,
                old_price=target_price,
                new_price=current_price
            )
            
            logger.info(f"Sent target price alert for product {product.id} to user {user.id}")
            
        except Exception as e:
            logger.error(f"Error sending target alert: {e}")

    @staticmethod
    async def _send_drop_alert(
        db: Session,
        watchlist: Watchlist,
        product: Product,
        current_price: float,
        drop_percentage: float
    ) -> None:
        """Send alert when price drops."""
        try:
            user = watchlist.user
            
            NotificationService(db).create_notification(
                user_id=user.id,
                notification_type="price_drop",
                title="Price Drop Alert",
                message=f"{product.name} price dropped by {drop_percentage:.1f}% to ₦{current_price:.2f}",
                data={"product_id": product.id, "drop_percentage": drop_percentage}
            )
            
            logger.info(f"Sent price drop alert for product {product.id} to user {user.id}")
            
        except Exception as e:
            logger.error(f"Error sending drop alert: {e}")
