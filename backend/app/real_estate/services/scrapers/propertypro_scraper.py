"""PropertyPro.ng scraper."""

from typing import Any, Dict, Optional

from bs4 import BeautifulSoup

from app.core.scraping.base_scraper import BaseScraper


class PropertyProScraper(BaseScraper):
    """Scraper for PropertyPro.ng."""

    def __init__(self):
        """Initialize PropertyPro scraper."""
        super().__init__(timeout=30, max_retries=3, rate_limit=2.0)

    async def extract_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract property data from PropertyPro."""
        html = await self.fetch(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        name_selectors = [
            "h1.single-property-title",
            ".property-title",
            "h1",
        ]
        name = self.extract_text_by_selectors(soup, name_selectors)

        price_selectors = [
            ".single-property-price",
            ".property-price",
            ".price-tag",
        ]
        price = self.extract_price_by_selectors(soup, price_selectors)

        location_selectors = [
            ".single-property-location",
            ".property-location",
            ".location",
        ]
        location = self.extract_text_by_selectors(soup, location_selectors)

        bedrooms = None
        bathrooms = None
        size_sqm = None

        details = soup.select(".property-details li, .single-property-details li")
        for detail in details:
            text = detail.get_text().lower()
            if "bedroom" in text:
                bedrooms = self.extract_number(text)
            elif "bathroom" in text:
                bathrooms = self.extract_number(text)
            elif "sqm" in text or "sq m" in text:
                size_sqm = self.extract_number(text)

        property_type_elem = soup.select_one(".property-type, .listing-type")
        property_type = property_type_elem.get_text().strip() if property_type_elem else "house"

        if not name or not price:
            fallback = self.smart_extract_data(soup, url)
            if fallback:
                name = name or fallback.get("name")
                price = price or fallback.get("price")

        if not name or not price:
            return None

        return {
            "name": name[:200],
            "price": price,
            "location": location[:200] if location else "Nigeria",
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "size_sqm": size_sqm,
            "property_type": property_type.lower() if property_type else "house",
            "listing_type": "sale",
            "url": url,
            "site": "propertypro.ng",
            "currency": "NGN",
        }
