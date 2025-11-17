"""Booking.com scraper implementation."""

import logging
from typing import Any, Dict, Optional

from app.core.scraping.base_scraper import BaseScraper
from app.utils.helpers import extract_price_from_text

logger = logging.getLogger(__name__)


class BookingScraper(BaseScraper):
    """Booking.com travel scraper for hotels and flights."""

    def __init__(self):
        """Initialize Booking scraper."""
        super().__init__(timeout=30, max_retries=3, rate_limit=2.0)

    async def extract_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract travel data from Booking.com URL."""
        html = await self.fetch(url)
        if not html:
            return None

        soup = self.parse(html)

        try:
            # Determine if it's a hotel or flight
            if "/hotel/" in url or "/accommodation/" in url:
                return await self._extract_hotel_data(soup, url)
            elif "/flights/" in url or "/flight/" in url:
                return await self._extract_flight_data(soup, url)
            else:
                # Try both
                hotel_data = await self._extract_hotel_data(soup, url)
                if hotel_data:
                    return hotel_data
                return await self._extract_flight_data(soup, url)

        except Exception as e:
            logger.error(f"Error extracting data from Booking.com URL {url}: {e}")
            return None

    async def _extract_hotel_data(self, soup, url: str) -> Optional[Dict[str, Any]]:
        """Extract hotel data from Booking.com."""
        # Hotel-specific selectors
        name_selectors = [
            "#hp_hotel_name",
            ".pp-header__title",
            "h2.hp__hotel-name",
            ".hotel-name",
            "h1[data-testid='title']",
            ".property-name"
        ]
        
        price_selectors = [
            ".prco-valign-middle-helper",
            ".bui-price-display__value",
            ".prco-text-nowrap-helper",
            ".sr-hotel__price-value",
            "[data-testid='price-and-discounted-price']",
            ".price"
        ]
        
        location_selectors = [
            ".hp_address_subtitle",
            ".hotel_address",
            "[data-testid='address']",
            ".property-location"
        ]

        rating_selectors = [
            ".bui-review-score__badge",
            ".review-score-badge",
            "[data-testid='review-score']"
        ]

        # Extract data
        name = self.extract_text_by_selectors(soup, name_selectors)
        price_text = self.extract_price_by_selectors(soup, price_selectors)
        location = self.extract_text_by_selectors(soup, location_selectors)
        rating_text = self.extract_text_by_selectors(soup, rating_selectors)

        # Fallback to smart extraction
        if not name or not price_text:
            fallback_data = self.smart_extract_data(soup, url)
            if fallback_data:
                name = name or fallback_data.get('name')
                price_text = price_text or fallback_data.get('price')

        if not name or not price_text:
            logger.warning(f"Could not extract required hotel data from {url}")
            return None

        price = extract_price_from_text(price_text)
        if not price:
            logger.warning(f"Could not parse price from text: {price_text}")
            return None

        # Parse rating
        rating = None
        if rating_text:
            try:
                rating = float(rating_text.split()[0])
            except (ValueError, IndexError):
                rating = None

        return {
            "type": "hotel",
            "name": name[:200],
            "location": location[:200] if location else "Unknown",
            "price_per_night": price,
            "total_price": price,  # Will be calculated based on dates
            "rating": rating,
            "url": url,
            "site": self.get_site_name(url),
            "currency": "NGN",
            "room_type": "standard",
            "guests": 2,
        }

    async def _extract_flight_data(self, soup, url: str) -> Optional[Dict[str, Any]]:
        """Extract flight data from Booking.com."""
        # Flight-specific selectors
        route_selectors = [
            ".flight-route",
            ".route-info",
            "[data-testid='flight-route']",
            ".flight-summary"
        ]
        
        price_selectors = [
            ".flight-price",
            ".price-display",
            "[data-testid='flight-price']",
            ".total-price"
        ]
        
        airline_selectors = [
            ".airline-name",
            ".carrier-name",
            "[data-testid='airline']"
        ]

        # Extract data
        route_text = self.extract_text_by_selectors(soup, route_selectors)
        price_text = self.extract_price_by_selectors(soup, price_selectors)
        airline = self.extract_text_by_selectors(soup, airline_selectors)

        # Fallback to smart extraction
        if not route_text or not price_text:
            fallback_data = self.smart_extract_data(soup, url)
            if fallback_data:
                route_text = route_text or fallback_data.get('name')
                price_text = price_text or fallback_data.get('price')

        if not route_text or not price_text:
            logger.warning(f"Could not extract required flight data from {url}")
            return None

        price = extract_price_from_text(price_text)
        if not price:
            logger.warning(f"Could not parse price from text: {price_text}")
            return None

        # Parse route (e.g., "Lagos to London" or "LOS - LHR")
        origin, destination = "LOS", "LHR"  # Default
        if route_text:
            route_parts = route_text.replace(" to ", "-").replace(" - ", "-").split("-")
            if len(route_parts) >= 2:
                origin = route_parts[0].strip()[:10]
                destination = route_parts[1].strip()[:10]

        return {
            "type": "flight",
            "origin": origin,
            "destination": destination,
            "airline": airline[:100] if airline else "Unknown",
            "price": price,
            "url": url,
            "site": self.get_site_name(url),
            "currency": "NGN",
            "flight_class": "economy",
            "passengers": 1,
        }