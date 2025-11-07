"""Email service using Resend."""

from typing import List, Optional

import httpx
from loguru import logger

from app.core.config import settings


class EmailService:
    """Email service using Resend API."""

    def __init__(self):
        """Initialize email service."""
        self.api_key = getattr(settings, "resend_api_key", None)
        self.base_url = "https://api.resend.com"
        self.from_email = getattr(settings, "from_email", "noreply@priceinsight.ng")

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
                logger.info(f"Email sent successfully to {to}")
                return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    async def send_price_alert(
        self,
        to: str,
        product_name: str,
        old_price: float,
        new_price: float,
        currency: str = "NGN",
    ) -> bool:
        """Send price drop alert email."""
        discount_percent = ((old_price - new_price) / old_price) * 100

        html_content = f"""
        <h2>Price Drop Alert! 🎉</h2>
        <p><strong>{product_name}</strong> price has dropped!</p>
        <p>Old Price: {currency}{old_price:,.2f}</p>
        <p>New Price: <strong>{currency}{new_price:,.2f}</strong></p>
        <p>You save: {currency}{old_price - new_price:,.2f} ({discount_percent:.1f}% off)</p>
        <p>Happy shopping!</p>
        """

        return await self.send_email(
            to=[to],
            subject=f"Price Drop: {product_name}",
            html_content=html_content,
        )


# Global email service instance
email_service = EmailService()
