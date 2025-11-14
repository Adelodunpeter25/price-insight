"""Change detection service for monitoring price changes and triggering alerts."""

from decimal import Decimal
from typing import List, Optional

import logging

logger = logging.getLogger(__name__)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.alerts.rules_engine import AlertRulesEngine
from app.core.models.alert import AlertHistory
from app.core.notifications.service import notification_service
from app.ecommerce.models import Product
from app.ecommerce.services.product_service import ProductService


class ChangeDetector:
    """Service for detecting price changes and triggering appropriate alerts."""

    def __init__(self, db: AsyncSession):
        """Initialize change detector with database session."""
        self.db = db
        self.product_service = ProductService(db)
        self.rules_engine = AlertRulesEngine(db)

    async def process_price_change(
        self,
        product_id: int,
        new_price: Decimal,
        currency: str = "NGN",
        availability: Optional[str] = None,
    ) -> List[AlertHistory]:
        """Process a price change and trigger alerts if needed."""

        logger.info(f"Processing price change for product {product_id}: ${new_price}")

        # Get previous price
        previous_price_entry = await self.product_service.get_latest_price(product_id)
        previous_price = previous_price_entry.price if previous_price_entry else None

        # Add new price to history
        await self.product_service.add_price_history(product_id, new_price, currency, availability)

        # Detect significant changes
        changes = await self._detect_changes(product_id, new_price, previous_price)

        # Evaluate alert rules
        triggered_alerts = await self.rules_engine.evaluate_price_change(
            product_id, new_price, previous_price
        )

        # Send notifications for triggered alerts
        if triggered_alerts:
            await notification_service.send_batch_notifications(triggered_alerts)

        # Log changes
        await self._log_changes(product_id, changes, triggered_alerts)

        return triggered_alerts

    async def _detect_changes(
        self, product_id: int, current_price: Decimal, previous_price: Optional[Decimal]
    ) -> dict:
        """Detect various types of changes."""

        changes = {
            "price_changed": False,
            "price_increased": False,
            "price_decreased": False,
            "significant_drop": False,
            "deal_detected": False,
            "price_change_percent": Decimal("0"),
        }

        if previous_price is None:
            changes["price_changed"] = True
            return changes

        if current_price != previous_price:
            changes["price_changed"] = True

            if current_price > previous_price:
                changes["price_increased"] = True
            else:
                changes["price_decreased"] = True

                # Calculate percentage change
                from app.utils.helpers import calculate_discount_percentage

                discount_percent = calculate_discount_percentage(previous_price, current_price)
                changes["price_change_percent"] = discount_percent

                # Check for significant drop (>5%)
                if discount_percent >= Decimal("5"):
                    changes["significant_drop"] = True

                # Check for deal (>10%)
                if discount_percent >= Decimal("10"):
                    changes["deal_detected"] = True

        return changes

    async def _log_changes(self, product_id: int, changes: dict, alerts: List[AlertHistory]):
        """Log detected changes and alerts."""

        if changes["price_changed"]:
            change_type = "increased" if changes["price_increased"] else "decreased"
            logger.info(f"Price {change_type} for product {product_id}")

            if changes["significant_drop"]:
                logger.info(
                    f"Significant price drop detected: {changes['price_change_percent']:.1f}%"
                )

            if changes["deal_detected"]:
                logger.info(f"Deal detected: {changes['price_change_percent']:.1f}% discount")

        if alerts:
            logger.info(f"Triggered {len(alerts)} alerts for product {product_id}")

    async def detect_availability_changes(self, product_id: int, current_availability: str) -> bool:
        """Detect availability changes (in stock, out of stock, etc.)."""

        # Get latest price history to check previous availability
        latest_entry = await self.product_service.get_latest_price(product_id)

        if not latest_entry or not latest_entry.availability:
            return False

        previous_availability = latest_entry.availability.lower()
        current_availability_lower = current_availability.lower()

        # Detect stock status changes
        stock_keywords = ["in stock", "available", "in-stock"]
        out_of_stock_keywords = ["out of stock", "unavailable", "sold out"]

        was_in_stock = any(keyword in previous_availability for keyword in stock_keywords)
        is_in_stock = any(keyword in current_availability_lower for keyword in stock_keywords)

        was_out_of_stock = any(
            keyword in previous_availability for keyword in out_of_stock_keywords
        )
        is_out_of_stock = any(
            keyword in current_availability_lower for keyword in out_of_stock_keywords
        )

        # Log availability changes
        if was_out_of_stock and is_in_stock:
            logger.info(f"Product {product_id} back in stock!")
            return True
        elif was_in_stock and is_out_of_stock:
            logger.info(f"Product {product_id} went out of stock")
            return True

        return False

    async def batch_process_products(self, products: List[Product]) -> dict:
        """Process multiple products for changes in batch."""

        results = {"processed": 0, "alerts_triggered": 0, "errors": 0}

        for product in products:
            try:
                # This would typically be called after scraping new data
                # For now, we'll just log that we would process it
                logger.debug(f"Would process product {product.id} for changes")
                results["processed"] += 1

            except Exception as e:
                logger.error(f"Error processing product {product.id}: {e}")
                results["errors"] += 1

        return results
