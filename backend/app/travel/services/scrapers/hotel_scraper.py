"""Hotel price scraper."""

from decimal import Decimal
from typing import Dict, Optional

from app.ecommerce.services.scraper_base import BaseScraper
from app.utils.currency import currency_converter


class HotelScraper(BaseScraper):
    """Generic hotel price scraper."""

    def extract_data(self, soup, url: str) -> Optional[Dict]:
        """Extract hotel data from HTML."""
        try:
            # Generic selectors for common travel sites
            price_selectors = [
                ".price", ".rate", ".cost", "[data-price]", ".amount",
                ".room-price", ".nightly-rate", ".hotel-price", ".total-price"
            ]
            
            rating_selectors = [
                ".rating", ".score", ".stars", "[data-rating]",
                ".hotel-rating", ".review-score"
            ]
            
            price_per_night = self._extract_price(soup, price_selectors)
            rating = self._extract_rating(soup, rating_selectors)
            
            if not price_per_night:
                return None
                
            return {
                "price_per_night": price_per_night,
                "total_price": price_per_night,  # Will be calculated based on nights
                "rating": rating,
                "currency": "NGN",  # Will be normalized by base scraper
                "site": self._get_site_name(url),
                "url": url
            }
            
        except Exception as e:
            self.logger.error(f"Failed to extract hotel data: {e}")
            return None

    def _extract_price(self, soup, selectors) -> Optional[Decimal]:
        """Extract price from soup using selectors."""
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                price = self._parse_price(text)
                if price:
                    return price
        return None

    def _extract_rating(self, soup, selectors) -> Optional[Decimal]:
        """Extract rating from soup using selectors."""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                rating = self._parse_rating(text)
                if rating:
                    return rating
        return None

    def _parse_price(self, text: str) -> Optional[Decimal]:
        """Parse price from text."""
        import re
        # Remove currency symbols and extract numbers
        price_match = re.search(r'[\d,]+\.?\d*', text.replace(',', ''))
        if price_match:
            try:
                return Decimal(price_match.group())
            except:
                pass
        return None

    def _parse_rating(self, text: str) -> Optional[Decimal]:
        """Parse rating from text."""
        import re
        # Extract rating (usually 1-5 or 1-10)
        rating_match = re.search(r'(\d+\.?\d*)', text)
        if rating_match:
            try:
                rating = Decimal(rating_match.group(1))
                if 0 <= rating <= 10:
                    return rating
            except:
                pass
        return None

    def _get_site_name(self, url: str) -> str:
        """Extract site name from URL."""
        from urllib.parse import urlparse
        return urlparse(url).netloc.replace('www.', '')