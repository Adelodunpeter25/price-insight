"""Travel alert service."""

import logging
from decimal import Decimal
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.notifications.service import NotificationService
from app.travel.models import Flight, Hotel
from app.travel.models.travel_alert import TravelAlertHistory, TravelAlertRule

logger = logging.getLogger(__name__)


class TravelAlertService:
    """Service for travel price alerts."""

    def __init__(self, db: AsyncSession):
        """Initialize service."""
        self.db = db
        self.notification_service = NotificationService()

    async def check_flight_alerts(self, flight: Flight, old_price: Decimal, new_price: Decimal):
        """Check and trigger flight price alerts."""
        query = select(TravelAlertRule).where(
            TravelAlertRule.flight_id == flight.id,
            TravelAlertRule.is_active == True
        )
        result = await self.db.execute(query)
        rules = result.scalars().all()

        for rule in rules:
            if await self._should_trigger_alert(rule, old_price, new_price):
                await self._trigger_alert(rule, flight, new_price)

    async def check_hotel_alerts(self, hotel: Hotel, old_price: Decimal, new_price: Decimal):
        """Check and trigger hotel price alerts."""
        query = select(TravelAlertRule).where(
            TravelAlertRule.hotel_id == hotel.id,
            TravelAlertRule.is_active == True
        )
        result = await self.db.execute(query)
        rules = result.scalars().all()

        for rule in rules:
            if await self._should_trigger_alert(rule, old_price, new_price):
                await self._trigger_alert(rule, hotel, new_price)

    async def _should_trigger_alert(self, rule: TravelAlertRule, old_price: Decimal, new_price: Decimal) -> bool:
        """Check if alert should be triggered."""
        if rule.rule_type == "price_drop" and rule.percentage_threshold:
            if old_price > 0:
                drop_percent = ((old_price - new_price) / old_price) * 100
                return drop_percent >= rule.percentage_threshold
        
        elif rule.rule_type == "threshold" and rule.threshold_value:
            return new_price <= rule.threshold_value
        
        return False

    async def _trigger_alert(self, rule: TravelAlertRule, item, price: Decimal):
        """Trigger alert notification."""
        item_type = "Flight" if rule.flight_id else "Hotel"
        item_name = f"{item.origin}-{item.destination}" if rule.flight_id else item.name
        
        message = f"{item_type} Alert: {item_name} price is now ${price}"
        
        # Create alert history
        alert_history = TravelAlertHistory(
            alert_rule_id=rule.id,
            flight_id=rule.flight_id,
            hotel_id=rule.hotel_id,
            trigger_value=price,
            message=message
        )
        
        self.db.add(alert_history)
        await self.db.commit()
        
        # Send notification
        await self.notification_service.send_notification(
            message=message,
            method=rule.notification_method,
            metadata={"rule_id": rule.id, "price": str(price)}
        )
        
        logger.info(f"Travel alert triggered: {message}")

    async def create_alert_rule(
        self,
        flight_id: int = None,
        hotel_id: int = None,
        rule_type: str = "price_drop",
        threshold_value: Decimal = None,
        percentage_threshold: Decimal = None,
        notification_method: str = "console"
    ) -> TravelAlertRule:
        """Create new travel alert rule."""
        rule = TravelAlertRule(
            flight_id=flight_id,
            hotel_id=hotel_id,
            rule_type=rule_type,
            threshold_value=threshold_value,
            percentage_threshold=percentage_threshold,
            notification_method=notification_method
        )
        
        self.db.add(rule)
        await self.db.commit()
        await self.db.refresh(rule)
        
        logger.info(f"Created travel alert rule: {rule}")
        return rule