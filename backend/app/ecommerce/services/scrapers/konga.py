"""Konga-specific scraper implementation."""

import logging
from typing import Any, Dict, Optional

from app.core.scraping.base_scraper import BaseScraper
from app.utils.helpers import extract_price_from_text

logger = logging.getLogger(__name__)


class KongaScraper(BaseScraper):
    """Konga product scraper."""

    def __init__(self):
        """Initialize Konga scraper."""
        super().__init__(timeout=30, max_retries=3, rate_limit=1.5)

    async def extract_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract product data from Konga URL."""
        html = await self.fetch(url)
        if not html:
            return None

        soup = self.parse(html)

        try:
            # Konga-specific selectors
            name_selectors = [
                ".product-title",
                "h1.product-name",
                ".pdp-product-name",
                ".product-details h1",
                "[data-testid='product-title']",
                ".item-title"
            ]
            
            price_selectors = [
                ".price",
                ".current-price",
                ".product-price",
                ".amount",
                ".price-current",
                ".sale-price",
                "[data-testid='price']"
            ]
            
            availability_selectors = [
                ".stock-status",
                ".availability",
                ".in-stock",
                ".stock-indicator",
                ".product-availability"
            ]

            # Try Konga-specific extraction
            name = self.extract_text_by_selectors(soup, name_selectors)
            price_text = self.extract_price_by_selectors(soup, price_selectors)
            availability = self.extract_text_by_selectors(soup, availability_selectors)

            # Fallback to smart extraction
            if not name or not price_text:
                fallback_data = self.smart_extract_data(soup, url)
                if fallback_data:
                    name = name or fallback_data.get('name')
                    price_text = price_text or fallback_data.get('price')
                    availability = availability or fallback_data.get('availability', 'Unknown')

            if not name or not price_text:
                logger.warning(f"Could not extract required data from {url}")
                return None

            price = extract_price_from_text(price_text)
            if not price:
                logger.warning(f"Could not parse price from text: {price_text}")
                return None

            return {
                "name": name[:200],
                "price": price,
                "url": url,
                "availability": availability or "Unknown",
                "site": self.get_site_name(url),
                "currency": "NGN",
            }

        except Exception as e:
            logger.error(f"Error extracting data from Konga URL {url}: {e}")
            return None