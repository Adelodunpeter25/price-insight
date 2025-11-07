"""Flight price scraper."""

from decimal import Decimal
from typing import Dict, Optional

from app.ecommerce.services.scraper_base import BaseScraper
from app.utils.currency import currency_converter


class FlightScraper(BaseScraper):
    """Generic flight price scraper."""

    def extract_data(self, soup, url: str) -> Optional[Dict]:
        """Extract flight data from HTML."""
        try:
            # Generic selectors for common travel sites
            price_selectors = [
                ".price", ".fare", ".cost", "[data-price]", ".amount",
                ".flight-price", ".total-price", ".booking-price"
            ]
            
            airline_selectors = [
                ".airline", ".carrier", ".operator", "[data-airline]",
                ".flight-operator", ".airline-name"
            ]
            
            price = self._extract_price(soup, price_selectors)
            airline = self._extract_text(soup, airline_selectors)
            
            if not price:
                return None
                
            return {
                "price": price,
                "airline": airline,
                "currency": "NGN",  # Will be normalized by base scraper
                "site": self._get_site_name(url),
                "url": url
            }
            
        except Exception as e:
            self.logger.error(f"Failed to extract flight data: {e}")
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

    def _extract_text(self, soup, selectors) -> Optional[str]:
        """Extract text from soup using selectors."""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
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

    def _get_site_name(self, url: str) -> str:
        """Extract site name from URL."""
        from urllib.parse import urlparse
        return urlparse(url).netloc.replace('www.', '')