"""Property watchlist alert service."""

import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.services.email_service import email_service
from app.core.services.notification_service import NotificationService
from app.real_estate.models.price_history import PropertyPriceHistory
from app.real_estate.models.watchlist import PropertyWatchlist

logger = logging.getLogger(__name__)


class PropertyWatchlistAlerts:
    """Service for checking and sending watchlist alerts."""

    @staticmethod
    async def check_watchlist_alerts(db: Session) -> int:
        """Check all watchlist items and send alerts."""
        watchlists = (
            db.query(PropertyWatchlist)
            .filter(PropertyWatchlist.is_active == True)
            .all()
        )

        alerts_sent = 0

        for watchlist in watchlists:
            try:
                latest_price = (
                    db.query(PropertyPriceHistory)
                    .filter(PropertyPriceHistory.property_id == watchlist.property_id)
                    .order_by(PropertyPriceHistory.created_at.desc())
                    .first()
                )

                if not latest_price:
                    continue

                current_price = float(latest_price.price)

                if watchlist.alert_on_target and watchlist.target_price:
                    if current_price <= float(watchlist.target_price):
                        await PropertyWatchlistAlerts._send_target_price_alert(
                            db, watchlist, current_price
                        )
                        alerts_sent += 1

                if watchlist.alert_on_any_drop:
                    previous_price = (
                        db.query(PropertyPriceHistory)
                        .filter(PropertyPriceHistory.property_id == watchlist.property_id)
                        .order_by(PropertyPriceHistory.created_at.desc())
                        .offset(1)
                        .first()
                    )

                    if previous_price and current_price < float(previous_price.price):
                        drop_percent = (
                            (float(previous_price.price) - current_price)
                            / float(previous_price.price)
                            * 100
                        )
                        await PropertyWatchlistAlerts._send_price_drop_alert(
                            db, watchlist, current_price, float(previous_price.price), drop_percent
                        )
                        alerts_sent += 1

            except Exception as e:
                logger.error(f"Failed to check watchlist {watchlist.id}: {e}")
                continue

        return alerts_sent

    @staticmethod
    async def _send_target_price_alert(
        db: Session, watchlist: PropertyWatchlist, current_price: float
    ):
        """Send target price reached alert."""
        notification_service = NotificationService(db)

        notification_service.create_notification(
            user_id=watchlist.user_id,
            notification_type="target_reached",
            title="Target Price Reached",
            message=f"{watchlist.property.name} is now at your target price of ₦{watchlist.target_price:,.2f}",
            data={
                "property_id": watchlist.property_id,
                "target_price": float(watchlist.target_price),
                "current_price": current_price,
            },
        )

        await email_service.send_price_alert(
            to=watchlist.user.email,
            product_name=watchlist.property.name,
            old_price=float(watchlist.target_price),
            new_price=current_price,
            currency="₦",
        )

    @staticmethod
    async def _send_price_drop_alert(
        db: Session,
        watchlist: PropertyWatchlist,
        current_price: float,
        previous_price: float,
        drop_percent: float,
    ):
        """Send price drop alert."""
        notification_service = NotificationService(db)

        notification_service.create_notification(
            user_id=watchlist.user_id,
            notification_type="price_drop",
            title="Property Price Drop",
            message=f"{watchlist.property.name} price dropped from ₦{previous_price:,.2f} to ₦{current_price:,.2f} ({drop_percent:.1f}% off)",
            data={
                "property_id": watchlist.property_id,
                "old_price": previous_price,
                "new_price": current_price,
                "drop_percent": drop_percent,
            },
        )

        await email_service.send_price_alert(
            to=watchlist.user.email,
            product_name=watchlist.property.name,
            old_price=previous_price,
            new_price=current_price,
            currency="₦",
        )
