"""Tolet.com.ng scraper."""

from typing import Any, Dict, Optional

from bs4 import BeautifulSoup

from app.core.scraping.base_scraper import BaseScraper


class ToletScraper(BaseScraper):
    """Scraper for Tolet.com.ng."""

    def __init__(self):
        """Initialize Tolet scraper."""
        super().__init__(timeout=30, max_retries=3, rate_limit=2.0)

    async def extract_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract property data from Tolet."""
        html = await self.fetch(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        name_selectors = [
            "h1.listing-title",
            ".property-name",
            "h1",
        ]
        name = self.extract_text_by_selectors(soup, name_selectors)

        price_selectors = [
            ".listing-price",
            ".property-price",
            ".price",
        ]
        price = self.extract_price_by_selectors(soup, price_selectors)

        location_selectors = [
            ".listing-location",
            ".property-address",
            ".location",
        ]
        location = self.extract_text_by_selectors(soup, location_selectors)

        bedrooms = None
        bathrooms = None
        size_sqm = None

        features = soup.select(".property-features li, .listing-features li")
        for feature in features:
            text = feature.get_text().lower()
            if "bedroom" in text:
                bedrooms = self.extract_number(text)
            elif "bathroom" in text:
                bathrooms = self.extract_number(text)
            elif "sqm" in text or "sq m" in text:
                size_sqm = self.extract_number(text)

        property_type = "apartment"
        type_elem = soup.select_one(".property-type, .listing-category")
        if type_elem:
            property_type = type_elem.get_text().strip().lower()

        listing_type = "rent"
        if "sale" in url.lower() or "buy" in url.lower():
            listing_type = "sale"

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
            "property_type": property_type,
            "listing_type": listing_type,
            "url": url,
            "site": "tolet.com.ng",
            "currency": "NGN",
        }
