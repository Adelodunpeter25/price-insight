"""Alert rules engine for evaluating notification triggers."""

from decimal import Decimal
from typing import List, Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.alert import AlertHistory, AlertRule
from app.ecommerce.models import PriceHistory
from app.utils.helpers import calculate_discount_percentage


class AlertRulesEngine:
    """Engine for evaluating alert rules and triggering notifications."""

    def __init__(self, db: AsyncSession):
        """Initialize rules engine with database session."""
        self.db = db

    async def evaluate_price_change(
        self, product_id: int, current_price: Decimal, previous_price: Optional[Decimal] = None
    ) -> List[AlertHistory]:
        """Evaluate all alert rules for a price change."""

        # Get all active alert rules for this product
        stmt = select(AlertRule).where(AlertRule.product_id == product_id, AlertRule.is_active)
        result = await self.db.execute(stmt)
        alert_rules = list(result.scalars().all())

        if not alert_rules:
            return []

        # Get previous price if not provided
        if previous_price is None:
            previous_price = await self._get_previous_price(product_id)

        triggered_alerts = []

        for rule in alert_rules:
            alert = await self._evaluate_rule(rule, current_price, previous_price)
            if alert:
                triggered_alerts.append(alert)

        return triggered_alerts

    async def _evaluate_rule(
        self, rule: AlertRule, current_price: Decimal, previous_price: Optional[Decimal]
    ) -> Optional[AlertHistory]:
        """Evaluate a single alert rule."""

        if rule.rule_type == "price_drop" and previous_price:
            return await self._evaluate_price_drop_rule(rule, current_price, previous_price)
        elif rule.rule_type == "threshold":
            return await self._evaluate_threshold_rule(rule, current_price)
        elif rule.rule_type == "deal_appeared":
            return await self._evaluate_deal_rule(rule, current_price, previous_price)

        return None

    async def _evaluate_price_drop_rule(
        self, rule: AlertRule, current_price: Decimal, previous_price: Decimal
    ) -> Optional[AlertHistory]:
        """Evaluate price drop percentage rule."""

        if current_price >= previous_price:
            return None  # No price drop

        discount_percent = calculate_discount_percentage(previous_price, current_price)

        if discount_percent >= (rule.percentage_threshold or Decimal("5")):
            message = (
                f"Price drop alert: {discount_percent:.1f}% decrease "
                f"from ${previous_price} to ${current_price}"
            )

            return await self._create_alert_history(rule, current_price, message)

        return None

    async def _evaluate_threshold_rule(
        self, rule: AlertRule, current_price: Decimal
    ) -> Optional[AlertHistory]:
        """Evaluate price threshold rule."""

        if rule.threshold_value and current_price <= rule.threshold_value:
            message = (
                f"Price threshold alert: Price dropped to ${current_price} "
                f"(below threshold of ${rule.threshold_value})"
            )

            return await self._create_alert_history(rule, current_price, message)

        return None

    async def _evaluate_deal_rule(
        self, rule: AlertRule, current_price: Decimal, previous_price: Optional[Decimal]
    ) -> Optional[AlertHistory]:
        """Evaluate deal appearance rule."""

        if not previous_price or current_price >= previous_price:
            return None

        # Check if this qualifies as a significant deal (>10% off)
        discount_percent = calculate_discount_percentage(previous_price, current_price)

        if discount_percent >= Decimal("10"):
            message = (
                f"Deal alert: Significant discount of {discount_percent:.1f}% "
                f"detected (${previous_price} → ${current_price})"
            )

            return await self._create_alert_history(rule, current_price, message)

        return None

    async def _create_alert_history(
        self, rule: AlertRule, trigger_value: Decimal, message: str
    ) -> AlertHistory:
        """Create alert history entry."""

        alert_history = AlertHistory(
            alert_rule_id=rule.id,
            product_id=rule.product_id,
            trigger_value=trigger_value,
            message=message,
            notification_sent=False,
        )

        self.db.add(alert_history)
        await self.db.commit()
        await self.db.refresh(alert_history)

        logger.info(f"Alert triggered: {message}")
        return alert_history

    async def _get_previous_price(self, product_id: int) -> Optional[Decimal]:
        """Get the most recent price before current one."""

        stmt = (
            select(PriceHistory.price)
            .where(PriceHistory.product_id == product_id)
            .order_by(PriceHistory.created_at.desc())
            .offset(1)  # Skip the most recent (current) price
            .limit(1)
        )

        result = await self.db.execute(stmt)
        price = result.scalar_one_or_none()
        return price

    async def create_alert_rule(
        self,
        product_id: int,
        rule_type: str,
        threshold_value: Optional[Decimal] = None,
        percentage_threshold: Optional[Decimal] = None,
        notification_method: str = "console",
    ) -> AlertRule:
        """Create a new alert rule."""

        rule = AlertRule(
            product_id=product_id,
            rule_type=rule_type,
            threshold_value=threshold_value,
            percentage_threshold=percentage_threshold,
            notification_method=notification_method,
        )

        self.db.add(rule)
        await self.db.commit()
        await self.db.refresh(rule)

        logger.info(f"Created alert rule: {rule_type} for product {product_id}")
        return rule
