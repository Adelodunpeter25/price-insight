"""Flight price scraper."""

from decimal import Decimal
from typing import Dict, Optional, Any

import logging

logger = logging.getLogger(__name__)

from app.core.scraping.base_scraper import BaseScraper
from app.utils.helpers import extract_price_from_text


class FlightScraper(BaseScraper):
    """Generic flight price scraper."""

    async def extract_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract flight data from URL."""
        html = await self.fetch(url)
        if not html:
            return None
            
        soup = self.parse(html)
        
        try:
            # Generic selectors for common travel sites
            price_selectors = [
                ".price",
                ".fare",
                ".cost",
                "[data-price]",
                ".amount",
                ".flight-price",
                ".total-price",
                ".booking-price",
                ".price-text",
                ".fare-price"
            ]

            airline_selectors = [
                ".airline",
                ".carrier",
                ".operator",
                "[data-airline]",
                ".flight-operator",
                ".airline-name",
                ".carrier-name"
            ]
            
            route_selectors = [
                ".route",
                ".flight-route",
                ".origin-destination",
                "[data-route]"
            ]

            price_text = self.extract_price_by_selectors(soup, price_selectors)
            if not price_text:
                logger.warning(f"Could not extract price from {url}")
                return None
                
            price = extract_price_from_text(price_text)
            if not price:
                logger.warning(f"Could not parse price from text: {price_text}")
                return None

            airline = self.extract_text_by_selectors(soup, airline_selectors) or "Unknown"
            route = self.extract_text_by_selectors(soup, route_selectors) or "Unknown"

            return {
                "name": f"Flight: {route} - {airline}",
                "price": price,
                "airline": airline,
                "route": route,
                "currency": "NGN",
                "site": self.get_site_name(url),
                "url": url,
            }

        except Exception as e:
            logger.error(f"Failed to extract flight data from {url}: {e}")
            return None


