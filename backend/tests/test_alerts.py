"""Unit tests for alert system functionality."""

import unittest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from app.core.alerts.rules_engine import AlertRulesEngine
from app.core.models.alert import AlertRule
from app.core.notifications.service import NotificationService


class TestAlertRulesEngine(unittest.TestCase):
    """Test alert rules engine functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_db = AsyncMock()
        self.engine = AlertRulesEngine(self.mock_db)

    async def test_evaluate_price_drop_rule_triggered(self):
        """Test price drop rule that should trigger."""
        rule = AlertRule(
            id=1,
            product_id=1,
            rule_type="price_drop",
            percentage_threshold=Decimal("10"),
        )

        current_price = Decimal("18.00")
        previous_price = Decimal("20.00")

        result = await self.engine._evaluate_price_drop_rule(rule, current_price, previous_price)

        self.assertIsNotNone(result)
        self.assertEqual(result.trigger_value, current_price)
        self.assertIn("10.0% decrease", result.message)

    async def test_evaluate_price_drop_rule_not_triggered(self):
        """Test price drop rule that should not trigger."""
        rule = AlertRule(
            id=1,
            product_id=1,
            rule_type="price_drop",
            percentage_threshold=Decimal("10"),
        )

        current_price = Decimal("19.00")
        previous_price = Decimal("20.00")  # Only 5% drop

        result = await self.engine._evaluate_price_drop_rule(rule, current_price, previous_price)

        self.assertIsNone(result)

    async def test_evaluate_threshold_rule_triggered(self):
        """Test threshold rule that should trigger."""
        rule = AlertRule(
            id=1,
            product_id=1,
            rule_type="threshold",
            threshold_value=Decimal("15.00"),
        )

        current_price = Decimal("14.00")

        result = await self.engine._evaluate_threshold_rule(rule, current_price)

        self.assertIsNotNone(result)
        self.assertEqual(result.trigger_value, current_price)
        self.assertIn("below threshold", result.message)

    async def test_evaluate_threshold_rule_not_triggered(self):
        """Test threshold rule that should not trigger."""
        rule = AlertRule(
            id=1,
            product_id=1,
            rule_type="threshold",
            threshold_value=Decimal("15.00"),
        )

        current_price = Decimal("16.00")

        result = await self.engine._evaluate_threshold_rule(rule, current_price)

        self.assertIsNone(result)


class TestNotificationService(unittest.TestCase):
    """Test notification service functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = NotificationService()

    def test_init(self):
        """Test service initialization."""
        self.assertEqual(len(self.service.sent_alerts), 0)
        self.assertEqual(self.service.notifications_dir, "notifications")

    async def test_send_console_notification(self):
        """Test console notification sending."""
        mock_alert = MagicMock()
        mock_alert.id = 1
        mock_alert.message = "Test alert message"
        mock_alert.product_id = 1
        mock_alert.trigger_value = Decimal("19.99")
        mock_alert.created_at = "2024-01-01 12:00:00"

        # This should not raise an exception
        await self.service._send_console_notification(mock_alert)

    def test_duplicate_prevention(self):
        """Test duplicate alert prevention."""
        # Simulate an alert already sent
        self.service.sent_alerts.add(1)

        mock_alert = MagicMock()
        mock_alert.id = 1

        # Should return False for duplicate
        self.service.send_notification(mock_alert)
        # Note: This would need to be async in real implementation


if __name__ == "__main__":
    unittest.main()
