"""Amazon-specific scraper implementation."""

from typing import Any, Dict, Optional

import logging

logger = logging.getLogger(__name__)

from app.core.scraping.base_scraper import BaseScraper
from app.utils.helpers import extract_price_from_text


class AmazonScraper(BaseScraper):
    """Amazon product scraper."""

    def __init__(self):
        """Initialize Amazon scraper."""
        super().__init__(timeout=30, max_retries=3)

    async def extract_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract product data from Amazon URL."""
        html = await self.fetch(url)
        if not html:
            return None

        soup = self.parse(html)

        try:
            # Extract product name
            name_selectors = [
                "#productTitle", 
                ".product-title", 
                "h1.a-size-large",
                "h1[data-automation-id='product-title']",
                ".pdp-product-name"
            ]
            name = self.extract_text_by_selectors(soup, name_selectors)
            
            if not name:
                logger.warning(f"Could not extract product name from {url}")
                return None

            # Extract price
            price_selectors = [
                ".a-price-whole",
                ".a-offscreen",
                ".a-price .a-offscreen",
                "#priceblock_dealprice",
                "#priceblock_ourprice",
                ".a-price-range",
                "[data-automation-id='product-price']",
                ".notranslate"
            ]
            
            price_text = self.extract_price_by_selectors(soup, price_selectors)
            if not price_text:
                logger.warning(f"Could not extract price from {url}")
                return None
                
            price = extract_price_from_text(price_text)
            if not price:
                logger.warning(f"Could not parse price from text: {price_text}")
                return None

            # Extract availability
            availability_selectors = [
                "#availability span", 
                ".a-color-success", 
                ".a-color-state",
                "#availability .a-color-state",
                "[data-automation-id='availability']"
            ]
            
            availability = self.extract_text_by_selectors(soup, availability_selectors) or "Unknown"

            return {
                "name": name,
                "price": price,
                "url": url,
                "availability": availability,
                "site": self.get_site_name(url),
                "currency": "NGN"
            }

        except Exception as e:
            logger.error(f"Error extracting data from Amazon URL {url}: {e}")
            return None
