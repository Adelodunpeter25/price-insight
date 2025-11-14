"""Hotel price scraper."""

from typing import Dict, Optional, Any

import logging

logger = logging.getLogger(__name__)

from app.core.scraping.base_scraper import BaseScraper
from app.utils.helpers import extract_price_from_text


class HotelScraper(BaseScraper):
    """Generic hotel price scraper."""

    async def extract_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract hotel data from URL."""
        html = await self.fetch(url)
        if not html:
            return None
            
        soup = self.parse(html)
        
        try:
            # Generic selectors for common hotel booking sites
            name_selectors = [
                ".hotel-name",
                ".property-name",
                ".accommodation-name",
                "h1",
                ".title",
                "[data-hotel-name]",
                ".hotel-title"
            ]
            
            price_selectors = [
                ".price",
                ".rate",
                ".cost",
                "[data-price]",
                ".amount",
                ".hotel-price",
                ".room-price",
                ".nightly-rate",
                ".price-per-night",
                ".total-price"
            ]

            location_selectors = [
                ".location",
                ".address",
                ".hotel-location",
                "[data-location]",
                ".property-location",
                ".destination"
            ]
            
            rating_selectors = [
                ".rating",
                ".stars",
                ".hotel-rating",
                "[data-rating]",
                ".star-rating"
            ]

            name = self.extract_text_by_selectors(soup, name_selectors)
            if not name:
                logger.warning(f"Could not extract hotel name from {url}")
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
            rating = self.extract_text_by_selectors(soup, rating_selectors) or "Not rated"

            return {
                "name": f"Hotel: {name}",
                "price": price,
                "hotel_name": name,
                "location": location,
                "rating": rating,
                "currency": "NGN",
                "site": self.get_site_name(url),
                "url": url,
            }

        except Exception as e:
            logger.error(f"Failed to extract hotel data from {url}: {e}")
            return None