"""Notification service for sending alerts via different channels."""

import os
from datetime import datetime
from typing import List, Set

from loguru import logger

from app.core.models.alert import AlertHistory


class NotificationService:
    """Service for dispatching notifications via multiple channels."""

    def __init__(self):
        """Initialize notification service."""
        self.sent_alerts: Set[int] = set()  # Track sent alerts to prevent duplicates
        self.notifications_dir = "notifications"
        self._ensure_notifications_dir()

    def _ensure_notifications_dir(self):
        """Ensure notifications directory exists."""
        if not os.path.exists(self.notifications_dir):
            os.makedirs(self.notifications_dir)

    async def send_notification(self, alert: AlertHistory) -> bool:
        """Send notification for an alert."""

        # Check for duplicates
        if alert.id in self.sent_alerts:
            logger.debug(f"Alert {alert.id} already sent, skipping")
            return False

        try:
            # Determine notification method
            method = getattr(alert.alert_rule, "notification_method", "console")

            if method == "console":
                await self._send_console_notification(alert)
            elif method == "file":
                await self._send_file_notification(alert)
            elif method == "email":
                await self._send_email_notification(alert)
            else:
                logger.warning(f"Unknown notification method: {method}")
                return False

            # Mark as sent
            self.sent_alerts.add(alert.id)
            return True

        except Exception as e:
            logger.error(f"Failed to send notification for alert {alert.id}: {e}")
            return False

    async def _send_console_notification(self, alert: AlertHistory):
        """Send notification to console/logs."""

        logger.info(f"🔔 ALERT: {alert.message}")
        logger.info(f"   Product ID: {alert.product_id}")
        logger.info(f"   Trigger Value: ${alert.trigger_value}")
        logger.info(f"   Time: {alert.created_at}")

    async def _send_file_notification(self, alert: AlertHistory):
        """Send notification to file."""

        filename = f"{self.notifications_dir}/alerts_{datetime.now().strftime('%Y%m%d')}.txt"

        notification_text = (
            f"[{alert.created_at}] PRICE ALERT\n"
            f"Product ID: {alert.product_id}\n"
            f"Message: {alert.message}\n"
            f"Trigger Value: ${alert.trigger_value}\n"
            f"Rule Type: {alert.alert_rule.rule_type}\n"
            f"{'='*50}\n\n"
        )

        with open(filename, "a", encoding="utf-8") as f:
            f.write(notification_text)

        logger.info(f"Alert written to file: {filename}")

    async def _send_email_notification(self, alert: AlertHistory):
        """Send email notification (placeholder implementation)."""

        # Placeholder for email implementation
        logger.info(f"📧 EMAIL ALERT: {alert.message}")
        logger.info("   (Email functionality not implemented yet)")

    async def send_batch_notifications(self, alerts: List[AlertHistory]) -> int:
        """Send multiple notifications in batch."""

        if not alerts:
            return 0

        sent_count = 0

        for alert in alerts:
            success = await self.send_notification(alert)
            if success:
                sent_count += 1

        logger.info(f"Sent {sent_count}/{len(alerts)} notifications")
        return sent_count

    async def send_daily_digest(self, alerts: List[AlertHistory]):
        """Send daily digest of all alerts."""

        if not alerts:
            logger.info("No alerts for daily digest")
            return

        # Group alerts by product
        alerts_by_product = {}
        for alert in alerts:
            product_id = alert.product_id
            if product_id not in alerts_by_product:
                alerts_by_product[product_id] = []
            alerts_by_product[product_id].append(alert)

        # Create digest
        digest_text = f"📊 DAILY PRICE ALERTS DIGEST - {datetime.now().strftime('%Y-%m-%d')}\n"
        digest_text += f"{'='*60}\n\n"

        for product_id, product_alerts in alerts_by_product.items():
            digest_text += f"Product ID {product_id}: {len(product_alerts)} alerts\n"
            for alert in product_alerts:
                digest_text += f"  • {alert.message}\n"
            digest_text += "\n"

        # Save digest to file
        filename = f"{self.notifications_dir}/daily_digest_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(digest_text)

        logger.info(f"Daily digest saved: {filename}")
        logger.info(
            f"📊 Daily digest: {len(alerts)} total alerts for {len(alerts_by_product)} products"
        )


# Global notification service instance
notification_service = NotificationService()
