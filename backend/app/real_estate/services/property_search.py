"""Property search and discovery service."""

import re
from typing import Dict, List, Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.core.scraping.scraper_factory import scraper_factory
from app.real_estate.models.price_history import PropertyPriceHistory
from app.real_estate.models.property import Property


class PropertySearchService:
    """Service for searching and discovering properties."""

    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate if string is a URL."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    @staticmethod
    def search_tracked_properties(
        db: Session, query: str, limit: int = 10
    ) -> List[Property]:
        """Search existing tracked properties."""
        return (
            db.query(Property)
            .filter(Property.name.ilike(f"%{query}%"), Property.is_active == True)
            .limit(limit)
            .all()
        )

    @staticmethod
    async def scrape_property_from_url(db: Session, url: str) -> Optional[Property]:
        """Scrape property from URL and add to database."""
        existing = db.query(Property).filter(Property.url == url).first()
        if existing:
            return existing

        scraper = scraper_factory.get_scraper(url, "real_estate")
        if not scraper:
            return None

        async with scraper:
            property_data = await scraper.scrape(url)

        if not property_data:
            return None

        property_obj = Property(
            name=property_data.get("name", "")[:200],
            property_type=property_data.get("property_type", "house"),
            location=property_data.get("location", "")[:200],
            bedrooms=property_data.get("bedrooms"),
            bathrooms=property_data.get("bathrooms"),
            size_sqm=property_data.get("size_sqm"),
            price=property_data.get("price", 0),
            price_per_sqm=property_data.get("price_per_sqm"),
            listing_type=property_data.get("listing_type", "sale"),
            currency=property_data.get("currency", "NGN"),
            agent=property_data.get("agent"),
            url=url,
            site=property_data.get("site", ""),
            features=property_data.get("features"),
            is_tracked=1,
        )

        db.add(property_obj)
        db.flush()

        price_history = PropertyPriceHistory(
            property_id=property_obj.id,
            price=property_data.get("price", 0),
            price_per_sqm=property_data.get("price_per_sqm"),
            currency=property_data.get("currency", "NGN"),
            source="scraper",
        )

        db.add(price_history)
        db.commit()
        db.refresh(property_obj)

        return property_obj

    @staticmethod
    async def search_and_scrape_properties(
        db: Session, property_name: str, max_results: int = 5
    ) -> List[Property]:
        """Search and scrape properties from multiple sites."""
        search_urls = [
            f"https://www.propertypro.ng/property-for-sale?search={property_name.replace(' ', '+')}",
            f"https://www.tolet.com.ng/search?location={property_name.replace(' ', '+')}",
        ]

        properties = []

        for search_url in search_urls:
            if len(properties) >= max_results:
                break

            try:
                scraper = scraper_factory.get_scraper(search_url, "real_estate")
                if not scraper:
                    continue

                async with scraper:
                    html = await scraper.fetch(search_url)

                if not html:
                    continue

                soup = BeautifulSoup(html, "html.parser")
                property_links = PropertySearchService._extract_property_links(
                    soup, search_url
                )

                for link in property_links[: max_results - len(properties)]:
                    property_obj = await PropertySearchService.scrape_property_from_url(
                        db, link
                    )
                    if property_obj:
                        properties.append(property_obj)

            except Exception:
                continue

        return properties

    @staticmethod
    def _extract_property_links(soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract property links from search results."""
        links = []
        domain = urlparse(base_url).netloc

        if "propertypro" in domain:
            for link in soup.select('a[href*="/property-for-"]'):
                href = link.get("href")
                if href and "/property-for-" in href:
                    full_url = href if href.startswith("http") else f"https://{domain}{href}"
                    links.append(full_url)

        elif "tolet" in domain:
            for link in soup.select('a[href*="/listings/"]'):
                href = link.get("href")
                if href and "/listings/" in href:
                    full_url = href if href.startswith("http") else f"https://{domain}{href}"
                    links.append(full_url)

        return list(set(links))
