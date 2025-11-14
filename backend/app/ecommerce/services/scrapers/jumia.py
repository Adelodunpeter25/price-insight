"""Jumia-specific scraper implementation."""

import logging
from typing import Any, Dict, Optional

from app.core.scraping.base_scraper import BaseScraper
from app.utils.helpers import extract_price_from_text

logger = logging.getLogger(__name__)


class JumiaScraper(BaseScraper):
    """Jumia product scraper."""

    def __init__(self):
        """Initialize Jumia scraper."""
        super().__init__(timeout=30, max_retries=3, rate_limit=2.0)

    async def extract_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract product data from Jumia URL."""
        html = await self.fetch(url)
        if not html:
            return None

        soup = self.parse(html)

        try:
            # Jumia-specific selectors
            name_selectors = [
                ".name",
                ".product-name", 
                "h1.-fs20",
                ".pdp-product-name",
                "h1[data-automation-id='product-title']",
                ".title"
            ]
            
            price_selectors = [
                ".price",
                ".current-price",
                ".-b.-ltr.-tal.-fs24",
                ".price-box .price",
                "span.-b.-ltr.-tal.-fs24.-prxs",
                ".notranslate",
                "[data-automation-id='product-price']"
            ]
            
            availability_selectors = [
                ".stock-status",
                ".availability", 
                ".in-stock",
                ".-df.-i-ctr.-fs14",
                ".stock-indicator"
            ]

            # Try Jumia-specific extraction
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
            logger.error(f"Error extracting data from Jumia URL {url}: {e}")
            return None