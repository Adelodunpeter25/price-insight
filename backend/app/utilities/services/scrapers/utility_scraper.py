"""Generic utility scraper for utilities and subscriptions."""

from decimal import Decimal
from typing import Dict, Optional
from urllib.parse import urlparse

from app.ecommerce.services.scraper_base import BaseScraper


class UtilityScraper(BaseScraper):
    """Generic utility scraper for utilities and subscriptions."""

    async def extract_data(self, url: str) -> Optional[Dict]:
        """Extract utility/subscription data from URL."""
        html = await self.fetch(url)
        if not html:
            return None

        soup = self.parse(html)

        try:
            # Generic selectors for utility/subscription sites
            name_selectors = [
                "h1",
                ".plan-name",
                ".service-title",
                ".title",
                "[data-testid='plan-title']",
                ".package-name",
                ".tariff-name",
            ]

            price_selectors = [
                ".price",
                ".cost",
                ".amount",
                "[data-price]",
                ".plan-price",
                ".tariff-rate",
                ".monthly-price",
                ".subscription-price",
            ]

            provider_selectors = [
                ".provider",
                ".company",
                ".brand",
                "[data-provider]",
                ".operator-name",
                ".service-provider",
            ]

            # Extract data
            name = self._extract_text(soup, name_selectors)
            price_text = self._extract_text(soup, price_selectors)
            provider = self._extract_text(soup, provider_selectors)

            if not name or not price_text:
                return None

            # Parse price
            price = self._parse_price(price_text)
            if not price:
                return None

            # Determine service type from URL and content
            service_type = self._determine_service_type(url, name.lower())

            # Determine billing type and cycle
            billing_type, billing_cycle = self._determine_billing_info(price_text.lower())

            return {
                "name": name,
                "price": price,
                "provider": provider or self._get_provider_from_url(url),
                "service_type": service_type,
                "billing_type": billing_type,
                "billing_cycle": billing_cycle,
                "currency": "NGN",  # Will be normalized by base scraper
                "site": self._get_site_name(url),
                "url": url,
            }

        except Exception as e:
            self.logger.error(f"Error extracting utility data from {url}: {e}")
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
            except (ValueError, TypeError):
                pass
        return None

    def _determine_service_type(self, url: str, name: str) -> str:
        """Determine service type from URL and name."""
        url_lower = url.lower()
        name_lower = name.lower()

        # Check URL patterns
        if any(word in url_lower for word in ["electricity", "power", "nepa", "phcn"]):
            return "electricity"
        elif any(word in url_lower for word in ["water", "waste"]):
            return "water"
        elif any(word in url_lower for word in ["internet", "broadband", "wifi"]):
            return "internet"
        elif any(word in url_lower for word in ["data", "mtn", "airtel", "glo", "9mobile"]):
            return "mobile_data"
        elif any(word in url_lower for word in ["dstv", "gotv", "cable", "tv"]):
            return "cable_tv"
        elif any(word in url_lower for word in ["netflix", "spotify", "showmax", "streaming"]):
            return "streaming"
        elif any(word in url_lower for word in ["microsoft", "adobe", "office", "software"]):
            return "software"

        # Check name patterns
        if any(word in name_lower for word in ["electricity", "power", "prepaid", "postpaid"]):
            return "electricity"
        elif any(word in name_lower for word in ["data", "gb", "mb"]):
            return "mobile_data"
        elif any(word in name_lower for word in ["premium", "basic", "family", "plan"]):
            return "streaming"
        else:
            return "subscription"  # Default

    def _determine_billing_info(self, price_text: str) -> tuple[str, Optional[str]]:
        """Determine billing type and cycle from price text."""
        if any(word in price_text for word in ["monthly", "per month", "/month"]):
            return "subscription", "monthly"
        elif any(word in price_text for word in ["yearly", "per year", "/year", "annual"]):
            return "subscription", "yearly"
        elif any(word in price_text for word in ["quarterly", "3 months"]):
            return "subscription", "quarterly"
        elif any(word in price_text for word in ["prepaid", "recharge"]):
            return "prepaid", None
        elif any(word in price_text for word in ["postpaid", "bill"]):
            return "postpaid", "monthly"
        else:
            return "subscription", "monthly"  # Default

    def _get_provider_from_url(self, url: str) -> str:
        """Extract provider from URL."""
        domain = urlparse(url).netloc.replace("www.", "")

        # Map common domains to providers
        provider_map = {
            "mtn.com.ng": "MTN",
            "airtel.com.ng": "Airtel",
            "glo.com": "Glo",
            "9mobile.com.ng": "9mobile",
            "netflix.com": "Netflix",
            "spotify.com": "Spotify",
            "dstv.com": "DSTV",
            "gotv.com.ng": "GOtv",
            "microsoft.com": "Microsoft",
            "adobe.com": "Adobe",
        }

        for domain_key, provider in provider_map.items():
            if domain_key in domain:
                return provider

        return domain.split(".")[0].title()

    def _get_site_name(self, url: str) -> str:
        """Extract site name from URL."""
        return urlparse(url).netloc.replace("www.", "")
