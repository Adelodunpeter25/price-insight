"""Scraper factory for creating appropriate scrapers based on URL."""

import logging
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

from app.core.scraping.base_scraper import BaseScraper
from app.ecommerce.services.scrapers.amazon import AmazonScraper
from app.ecommerce.services.scrapers.generic import COMMON_SELECTORS, GenericScraper
from app.ecommerce.services.scrapers.jumia import JumiaScraper
from app.ecommerce.services.scrapers.konga import KongaScraper
from app.real_estate.services.scrapers.property_scraper import PropertyScraper
from app.travel.services.scrapers.flight_scraper import FlightScraper
from app.travel.services.scrapers.hotel_scraper import HotelScraper
from app.utilities.services.scrapers.utility_scraper import UtilityScraper


class ScraperFactory:
    """Factory for creating appropriate scrapers based on URL patterns."""

    def __init__(self):
        """Initialize scraper factory with site configurations."""
        self.ecommerce_sites = {
            "amazon.com": AmazonScraper,
            "amazon.ng": AmazonScraper,
            "jumia.com.ng": JumiaScraper,
            "jumia.ng": JumiaScraper,
            "konga.com": KongaScraper,
            "jiji.ng": self._create_jiji_scraper,
        }

        self.travel_sites = {
            "booking.com": HotelScraper,
            "hotels.com": HotelScraper,
            "expedia.com": FlightScraper,
            "kayak.com": FlightScraper,
            "skyscanner.com": FlightScraper,
        }

        self.real_estate_sites = {
            "propertypro.ng": PropertyScraper,
            "tolet.com.ng": PropertyScraper,
            "privateproperty.com.ng": PropertyScraper,
        }

        self.utility_sites = {
            "ikedc.com": UtilityScraper,
            "ekedc.com": UtilityScraper,
            "mtn.ng": UtilityScraper,
            "airtel.ng": UtilityScraper,
        }

    def get_scraper(self, url: str, category: str = "auto") -> Optional[BaseScraper]:
        """Get appropriate scraper for URL and category."""
        try:
            domain = urlparse(url).netloc.replace("www.", "")

            if category == "auto":
                category = self._detect_category(domain)

            if category == "ecommerce":
                return self._get_ecommerce_scraper(domain)
            elif category == "travel":
                return self._get_travel_scraper(domain)
            elif category == "real_estate":
                return self._get_real_estate_scraper(domain)
            elif category == "utilities":
                return self._get_utility_scraper(domain)
            else:
                logger.warning(f"Unknown category '{category}' for {url}")
                return self._get_generic_scraper(domain)

        except Exception as e:
            logger.error(f"Failed to create scraper for {url}: {e}")
            return None

    def _detect_category(self, domain: str) -> str:
        """Auto-detect category based on domain."""
        if domain in self.ecommerce_sites:
            return "ecommerce"
        elif domain in self.travel_sites:
            return "travel"
        elif domain in self.real_estate_sites:
            return "real_estate"
        elif domain in self.utility_sites:
            return "utilities"
        else:
            # Default to ecommerce for unknown sites
            return "ecommerce"

    def _get_ecommerce_scraper(self, domain: str) -> BaseScraper:
        """Get e-commerce scraper for domain."""
        scraper_class = self.ecommerce_sites.get(domain)
        if scraper_class:
            if callable(scraper_class):
                return scraper_class()
            else:
                return scraper_class
        return self._get_generic_scraper(domain)

    def _get_travel_scraper(self, domain: str) -> BaseScraper:
        """Get travel scraper for domain."""
        scraper_class = self.travel_sites.get(domain)
        if scraper_class:
            return scraper_class()
        return FlightScraper()  # Default to flight scraper

    def _get_real_estate_scraper(self, domain: str) -> BaseScraper:
        """Get real estate scraper for domain."""
        scraper_class = self.real_estate_sites.get(domain)
        if scraper_class:
            return scraper_class()
        return PropertyScraper()

    def _get_utility_scraper(self, domain: str) -> BaseScraper:
        """Get utility scraper for domain."""
        scraper_class = self.utility_sites.get(domain)
        if scraper_class:
            return scraper_class()
        return UtilityScraper()

    def _get_generic_scraper(self, domain: str) -> GenericScraper:
        """Get generic scraper with site-specific selectors."""
        # Try to match common e-commerce platforms
        if "shopify" in domain:
            return GenericScraper(COMMON_SELECTORS["shopify"])
        elif any(keyword in domain for keyword in ["shop", "store", "buy"]):
            return GenericScraper(COMMON_SELECTORS["woocommerce"])
        else:
            # Default generic selectors
            return GenericScraper(
                {
                    "name": [".product-title", ".title", "h1", ".name", ".product-name"],
                    "price": [".price", ".cost", ".amount", "[data-price]", ".money"],
                    "availability": [".stock", ".availability", ".in-stock", ".out-of-stock"],
                }
            )



    def _create_jiji_scraper(self) -> GenericScraper:
        """Create Jiji-specific scraper."""
        return GenericScraper(
            {
                "name": [".qa-advert-title", ".title", "h1"],
                "price": [".qa-advert-price", ".price", ".amount"],
                "availability": [".status", ".availability"],
            }
        )


# Global factory instance
scraper_factory = ScraperFactory()
