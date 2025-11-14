"""Generic e-commerce scraper with configurable selectors."""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

from app.core.scraping.base_scraper import BaseScraper
from app.utils.helpers import extract_price_from_text


class GenericScraper(BaseScraper):
    """Generic e-commerce scraper with configurable selectors."""

    def __init__(self, selectors: Dict[str, List[str]] = None):
        """Initialize generic scraper with custom selectors.

        Args:
            selectors: Dict with 'name', 'price', 'availability' keys
                      containing lists of CSS selectors to try
        """
        super().__init__(timeout=30, max_retries=3)
        self.selectors = selectors or {}
        
    def auto_detect_selectors(self, url: str) -> Dict[str, List[str]]:
        """Auto-detect selectors based on URL domain."""
        domain = self.get_site_name(url).lower()
        
        for platform, selectors in COMMON_SELECTORS.items():
            if platform in domain or any(keyword in domain for keyword in [platform]):
                return selectors
                
        # Check for common e-commerce platforms
        if any(keyword in domain for keyword in ['shopify', 'myshopify']):
            return COMMON_SELECTORS['shopify']
        elif 'jumia' in domain:
            return COMMON_SELECTORS['jumia']
        elif 'konga' in domain:
            return COMMON_SELECTORS['konga']
            
        # Return empty dict for full fallback to smart extraction
        return {}

    async def extract_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract product data using configured selectors with fallbacks."""
        html = await self.fetch(url)
        if not html:
            return None

        soup = self.parse(html)

        try:
            # Auto-detect selectors if not provided
            if not self.selectors:
                self.selectors = self.auto_detect_selectors(url)
                
            # Try configured selectors first
            name = self.extract_text_by_selectors(soup, self.selectors.get("name", []))
            price_text = self.extract_price_by_selectors(soup, self.selectors.get("price", []))
            availability = self.extract_text_by_selectors(soup, self.selectors.get("availability", []))

            # Fallback to smart extraction if configured selectors fail
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
            logger.error(f"Error extracting data from {url}: {e}")
            return None


# Comprehensive selector configurations for popular sites
COMMON_SELECTORS = {
    "jumia": {
        "name": [".name", ".product-name", "h1.-fs20", ".pdp-product-name"],
        "price": [".price", ".current-price", ".-b.-ltr.-tal.-fs24", ".price-box .price"],
        "availability": [".stock-status", ".availability", ".in-stock"],
    },
    "konga": {
        "name": [".product-title", "h1.product-name", ".pdp-product-name"],
        "price": [".price", ".current-price", ".product-price", ".amount"],
        "availability": [".stock-status", ".availability"],
    },
    "shopify": {
        "name": [".product-title", ".product__title", "h1.product-single__title", ".product-form__title"],
        "price": [".price", ".product-price", ".money", ".product__price", ".price--current"],
        "availability": [".product-form__availability", ".stock-status", ".product__availability"],
    },
    "woocommerce": {
        "name": [".product_title", ".entry-title", "h1.product_title", ".woocommerce-product-title"],
        "price": [".price", ".woocommerce-Price-amount", ".amount", ".price ins .amount"],
        "availability": [".stock", ".availability", ".woocommerce-stock-status"],
    },
    "magento": {
        "name": [".page-title", ".product-name", "h1.page-title-wrapper"],
        "price": [".price", ".regular-price", ".special-price", ".price-box .price"],
        "availability": [".stock", ".availability", ".stock-status"],
    },
}
