"""Real estate property scraper."""

from typing import Dict, Optional, Any

import logging

logger = logging.getLogger(__name__)

from app.core.scraping.base_scraper import BaseScraper
from app.utils.helpers import extract_price_from_text


class PropertyScraper(BaseScraper):
    """Generic real estate property scraper."""

    async def extract_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract property data from URL."""
        html = await self.fetch(url)
        if not html:
            return None
            
        soup = self.parse(html)
        
        try:
            # Generic selectors for property listing sites
            title_selectors = [
                ".property-title",
                ".listing-title",
                ".property-name",
                "h1",
                ".title",
                "[data-property-title]",
                ".property-header h1"
            ]
            
            price_selectors = [
                ".price",
                ".property-price",
                ".listing-price",
                ".cost",
                "[data-price]",
                ".amount",
                ".rent-price",
                ".sale-price",
                ".property-cost"
            ]

            location_selectors = [
                ".location",
                ".address",
                ".property-location",
                "[data-location]",
                ".property-address",
                ".area",
                ".neighborhood"
            ]
            
            type_selectors = [
                ".property-type",
                ".listing-type",
                "[data-property-type]",
                ".type",
                ".category"
            ]
            
            bedrooms_selectors = [
                ".bedrooms",
                ".beds",
                "[data-bedrooms]",
                ".bedroom-count",
                ".bed-count"
            ]

            title = self.extract_text_by_selectors(soup, title_selectors)
            if not title:
                logger.warning(f"Could not extract property title from {url}")
                return None

            price_text = self.extract_price_by_selectors(soup, price_selectors)
            if not price_text:
                logger.warning(f"Could not extract price from {url}")
                return None
                
            price = extract_price_from_text(price_text)
            if not price:
                logger.warning(f"Could not parse price from text: {price_text}")
                return None

            location = self.extract_text_by_selectors(soup, location_selectors) or "Unknown"
            property_type = self.extract_text_by_selectors(soup, type_selectors) or "Unknown"
            bedrooms = self.extract_text_by_selectors(soup, bedrooms_selectors) or "Unknown"

            return {
                "name": f"Property: {title}",
                "price": price,
                "title": title,
                "location": location,
                "property_type": property_type,
                "bedrooms": bedrooms,
                "currency": "NGN",
                "site": self.get_site_name(url),
                "url": url,
            }

        except Exception as e:
            logger.error(f"Failed to extract property data from {url}: {e}")
            return None