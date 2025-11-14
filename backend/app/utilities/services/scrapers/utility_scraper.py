"""Utility service scraper."""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

from app.core.scraping.base_scraper import BaseScraper
from app.utils.helpers import extract_price_from_text


class UtilityScraper(BaseScraper):
    """Generic utility service scraper."""

    async def extract_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract utility service data from URL."""
        html = await self.fetch(url)
        if not html:
            return None

        soup = self.parse(html)

        try:
            # Generic selectors for utility service sites
            name_selectors = [
                ".service-name",
                ".plan-name",
                ".package-name",
                "h1",
                ".title",
                "[data-service-name]",
                ".service-title",
            ]

            price_selectors = [
                ".price",
                ".rate",
                ".cost",
                "[data-price]",
                ".amount",
                ".service-price",
                ".plan-price",
                ".monthly-rate",
                ".tariff",
            ]

            service_type_selectors = [
                ".service-type",
                ".category",
                "[data-service-type]",
                ".type",
                ".plan-type",
            ]

            description_selectors = [
                ".description",
                ".service-description",
                ".plan-description",
                ".details",
                ".service-details",
            ]

            name = self.extract_text_by_selectors(soup, name_selectors)
            if not name:
                logger.warning(f"Could not extract service name from {url}")
                return None

            price_text = self.extract_price_by_selectors(soup, price_selectors)
            if not price_text:
                logger.warning(f"Could not extract price from {url}")
                return None

            price = extract_price_from_text(price_text)
            if not price:
                logger.warning(f"Could not parse price from text: {price_text}")
                return None

            service_type = self.extract_text_by_selectors(soup, service_type_selectors) or "Unknown"
            description = (
                self.extract_text_by_selectors(soup, description_selectors) or "No description"
            )

            return {
                "name": f"Service: {name}",
                "price": price,
                "service_name": name,
                "service_type": service_type,
                "description": description,
                "currency": "NGN",
                "site": self.get_site_name(url),
                "url": url,
            }

        except Exception as e:
            logger.error(f"Failed to extract utility service data from {url}: {e}")
            return None
