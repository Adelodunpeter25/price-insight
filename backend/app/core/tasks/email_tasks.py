"""Celery tasks for email sending."""

import logging
from typing import Optional

from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def send_price_alert_task(
    self,
    to: str,
    product_name: str,
    old_price: float,
    new_price: float,
    currency: str = "₦"
):
    """Send price alert email (Celery task)."""
    try:
        from app.core.services.email_service import email_service
        import asyncio
        
        result = asyncio.run(
            email_service.send_price_alert(
                to=to,
                product_name=product_name,
                old_price=old_price,
                new_price=new_price,
                currency=currency
            )
        )
        
        if not result:
            raise Exception("Email sending failed")
        
        logger.info(f"Price alert email sent to {to}")
        return {"status": "sent", "to": to}
        
    except Exception as e:
        logger.error(f"Failed to send price alert email: {e}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task(bind=True, max_retries=3)
def send_deal_notification_task(
    self,
    to: str,
    item_name: str,
    category: str,
    price: float,
    provider: str,
    discount_percent: Optional[float] = None,
    currency: str = "₦"
):
    """Send deal notification email (Celery task)."""
    try:
        from app.core.services.email_service import email_service
        import asyncio
        
        result = asyncio.run(
            email_service.send_deal_notification(
                to=to,
                item_name=item_name,
                category=category,
                price=price,
                provider=provider,
                discount_percent=discount_percent,
                currency=currency
            )
        )
        
        if not result:
            raise Exception("Email sending failed")
        
        logger.info(f"Deal notification email sent to {to}")
        return {"status": "sent", "to": to}
        
    except Exception as e:
        logger.error(f"Failed to send deal notification email: {e}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task(bind=True, max_retries=3)
def send_welcome_email_task(self, to: str, user_name: str):
    """Send welcome email (Celery task)."""
    try:
        from app.core.services.email_service import email_service
        import asyncio
        
        result = asyncio.run(
            email_service.send_welcome_email(to=to, user_name=user_name)
        )
        
        if not result:
            raise Exception("Email sending failed")
        
        logger.info(f"Welcome email sent to {to}")
        return {"status": "sent", "to": to}
        
    except Exception as e:
        logger.error(f"Failed to send welcome email: {e}")
        raise self.retry(exc=e, countdown=60)
