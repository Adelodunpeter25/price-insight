"""Email service using Resend."""

from pathlib import Path
from typing import List, Optional

import httpx
from jinja2 import Environment, FileSystemLoader

from app.core.config import settings
from app.core.logging import log_event

import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Email service using Resend API."""

    def __init__(self):
        """Initialize email service."""
        self.api_key = getattr(settings, "resend_api_key", None)
        self.base_url = "https://api.resend.com"
        self.from_email = getattr(settings, "from_email", "noreply@priceinsight.ng")

        # Setup Jinja2 template environment
        template_dir = Path(__file__).parent.parent.parent / "templates"
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

    async def send_email(
        self,
        to: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """Send email using Resend API."""
        if not self.api_key:
            logger.warning("Resend API key not configured")
            return False

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/emails",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "from": self.from_email,
                        "to": to,
                        "subject": subject,
                        "html": html_content,
                        "text": text_content or html_content,
                    },
                )
                response.raise_for_status()
                log_event("email_sent", {"to": to, "subject": subject})
                logger.info(f"Email sent successfully to {to}")
                return True

        except Exception as e:
            log_event("email_failed", {"error": str(e), "to": to})
            logger.error(f"Failed to send email: {e}")
            return False

    def render_template(self, template_name: str, **context) -> str:
        """Render HTML template with context."""
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            log_event("template_render_failed", {"template": template_name, "error": str(e)})
            logger.error(f"Failed to render template {template_name}: {e}")
            return "<p>Error rendering email template</p>"

    async def send_price_alert(
        self,
        to: str,
        product_name: str,
        old_price: float,
        new_price: float,
        currency: str = "₦",
    ) -> bool:
        """Send price drop alert email."""
        discount_percent = ((old_price - new_price) / old_price) * 100
        savings = old_price - new_price

        html_content = self.render_template(
            "price_alert.html",
            product_name=product_name,
            old_price=f"{old_price:,.2f}",
            new_price=f"{new_price:,.2f}",
            currency=currency,
            savings=f"{savings:,.2f}",
            discount_percent=f"{discount_percent:.1f}",
        )

        return await self.send_email(
            to=[to],
            subject=f"Price Drop: {product_name}",
            html_content=html_content,
        )

    async def send_welcome_email(self, to: str, user_name: str) -> bool:
        """Send welcome email to new user."""
        html_content = self.render_template(
            "welcome.html",
            user_name=user_name,
        )

        return await self.send_email(
            to=[to],
            subject="Welcome to Price Insight!",
            html_content=html_content,
        )

    async def send_deal_notification(
        self,
        to: str,
        item_name: str,
        category: str,
        price: float,
        provider: str,
        deal_type: str = "Hot Deal",
        discount_percent: Optional[float] = None,
        currency: str = "₦",
    ) -> bool:
        """Send deal notification email."""
        html_content = self.render_template(
            "deal_notification.html",
            item_name=item_name,
            category=category,
            price=f"{price:,.2f}",
            provider=provider,
            deal_type=deal_type,
            discount_percent=f"{discount_percent:.1f}" if discount_percent else None,
            currency=currency,
        )

        return await self.send_email(
            to=[to],
            subject=f"🔥 {deal_type}: {item_name}",
            html_content=html_content,
        )


# Global email service instance
email_service = EmailService()
