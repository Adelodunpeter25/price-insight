"""Generic e-commerce scraper with configurable selectors."""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

from app.core.scraping.base_scraper import BaseScraper
from app.utils.helpers import extract_price_from_text


class GenericScraper(BaseScraper):
    """Generic e-commerce scraper with configurable selectors."""

    def __init__(self, selectors: Dict[str, List[str]]):
        """Initialize generic scraper with custom selectors.

        Args:
            selectors: Dict with 'name', 'price', 'availability' keys
                      containing lists of CSS selectors to try
        """
        super().__init__(timeout=30, max_retries=3)
        self.selectors = selectors

    async def extract_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract product data using configured selectors."""
        html = await self.fetch(url)
        if not html:
            return None

        soup = self.parse(html)

        try:
            # Extract product name
            name = self.extract_text_by_selectors(soup, self.selectors.get("name", []))
            if not name:
                logger.warning(f"Could not extract product name from {url}")
                return None

            # Extract price
            price_text = self.extract_price_by_selectors(soup, self.selectors.get("price", []))
            if not price_text:
                logger.warning(f"Could not extract price from {url}")
                return None

            price = extract_price_from_text(price_text)
            if not price:
                logger.warning(f"Could not parse price from text: {price_text}")
                return None

            # Extract availability (optional)
            availability = (
                self.extract_text_by_selectors(soup, self.selectors.get("availability", []))
                or "Unknown"
            )

            # Determine site from URL
            site = self.get_site_name(url)

            return {
                "name": name,
                "price": price,
                "url": url,
                "availability": availability,
                "site": site,
                "currency": "NGN",
            }

        except Exception as e:
            logger.error(f"Error extracting data from {url}: {e}")
            return None


# Common selector configurations for popular sites
COMMON_SELECTORS = {
    "shopify": {
        "name": [".product-title", ".product__title", "h1.product-single__title"],
        "price": [".price", ".product-price", ".money", ".product__price"],
        "availability": [".product-form__availability", ".stock-status"],
    },
    "woocommerce": {
        "name": [".product_title", ".entry-title", "h1.product_title"],
        "price": [".price", ".woocommerce-Price-amount", ".amount"],
        "availability": [".stock", ".availability"],
    },
}
