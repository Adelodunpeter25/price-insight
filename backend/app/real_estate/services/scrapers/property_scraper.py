"""Generic property scraper."""

from decimal import Decimal
from typing import Dict, Optional
from urllib.parse import urlparse

from app.ecommerce.services.scraper_base import BaseScraper


class PropertyScraper(BaseScraper):
    """Generic property scraper for real estate sites."""

    async def extract_data(self, url: str) -> Optional[Dict]:
        """Extract property data from URL."""
        html = await self.fetch(url)
        if not html:
            return None

        soup = self.parse(html)

        try:
            # Generic selectors for property sites
            name_selectors = [
                "h1", ".property-title", ".listing-title", ".title",
                "[data-testid='property-title']", ".property-name"
            ]
            
            price_selectors = [
                ".price", ".cost", ".amount", "[data-price]",
                ".property-price", ".listing-price", ".rent-price"
            ]
            
            location_selectors = [
                ".location", ".address", ".area", "[data-location]",
                ".property-location", ".listing-location"
            ]
            
            bedrooms_selectors = [
                ".bedrooms", ".beds", "[data-bedrooms]", ".bed-count"
            ]
            
            bathrooms_selectors = [
                ".bathrooms", ".baths", "[data-bathrooms]", ".bath-count"
            ]

            # Extract data
            name = self._extract_text(soup, name_selectors)
            price_text = self._extract_text(soup, price_selectors)
            location = self._extract_text(soup, location_selectors)
            bedrooms_text = self._extract_text(soup, bedrooms_selectors)
            bathrooms_text = self._extract_text(soup, bathrooms_selectors)

            if not name or not price_text:
                return None

            # Parse price
            price = self._parse_price(price_text)
            if not price:
                return None

            # Parse bedrooms/bathrooms
            bedrooms = self._parse_number(bedrooms_text) if bedrooms_text else None
            bathrooms = self._parse_number(bathrooms_text) if bathrooms_text else None

            # Determine property type from name/description
            property_type = self._determine_property_type(name.lower())
            
            # Determine listing type
            listing_type = self._determine_listing_type(price_text.lower())

            return {
                "name": name,
                "price": price,
                "location": location or "Unknown",
                "property_type": property_type,
                "listing_type": listing_type,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "currency": "NGN",  # Will be normalized by base scraper
                "site": self._get_site_name(url),
                "url": url,
            }

        except Exception as e:
            self.logger.error(f"Error extracting property data from {url}: {e}")
            return None

    def _extract_text(self, soup, selectors) -> Optional[str]:
        """Extract text using selectors."""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if text:
                    return text
        return None

    def _parse_price(self, text: str) -> Optional[Decimal]:
        """Parse price from text."""
        import re
        # Remove common words and extract numbers
        text = text.replace(",", "").replace(" ", "")
        price_match = re.search(r"[\d,]+\.?\d*", text)
        if price_match:
            try:
                return Decimal(price_match.group())
            except:
                pass
        return None

    def _parse_number(self, text: str) -> Optional[int]:
        """Parse number from text."""
        import re
        number_match = re.search(r"\d+", text)
        if number_match:
            try:
                return int(number_match.group())
            except:
                pass
        return None

    def _determine_property_type(self, name: str) -> str:
        """Determine property type from name."""
        if any(word in name for word in ["apartment", "flat", "condo"]):
            return "apartment"
        elif any(word in name for word in ["house", "bungalow", "duplex", "villa"]):
            return "house"
        elif any(word in name for word in ["land", "plot", "acre"]):
            return "land"
        elif any(word in name for word in ["office", "shop", "warehouse", "commercial"]):
            return "commercial"
        else:
            return "house"  # Default

    def _determine_listing_type(self, price_text: str) -> str:
        """Determine if property is for sale or rent."""
        if any(word in price_text for word in ["rent", "monthly", "per month", "/month"]):
            return "rent"
        else:
            return "sale"

    def _get_site_name(self, url: str) -> str:
        """Extract site name from URL."""
        return urlparse(url).netloc.replace("www.", "")