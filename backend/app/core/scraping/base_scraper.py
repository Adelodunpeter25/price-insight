"""Enhanced base scraper with rate limiting and error handling."""

import asyncio
import logging
import random
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from app.utils.currency import currency_converter
from app.utils.helpers import validate_url

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Enhanced base scraper with rate limiting and robust error handling."""

    def __init__(self, timeout: int = 30, max_retries: int = 3, rate_limit: float = 1.0):
        """Initialize scraper with configuration."""
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limit = rate_limit
        self.session = None
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]

    async def __aenter__(self) -> "BaseScraper":
        """Async context manager entry."""
        self.session = httpx.AsyncClient(
            timeout=self.timeout,
            headers=self._get_headers(),
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        if self.session:
            await self.session.aclose()

    def _get_headers(self) -> Dict[str, str]:
        """Get randomized headers."""
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    async def fetch(self, url: str) -> Optional[str]:
        """Fetch HTML content with rate limiting and retry logic."""
        if not validate_url(url):
            logger.error(f"Invalid URL: {url}")
            return None

        for attempt in range(self.max_retries):
            try:
                # Rate limiting
                await asyncio.sleep(self.rate_limit + random.uniform(0, 0.5))

                response = await self.session.get(url, headers=self._get_headers())
                response.raise_for_status()

                logger.info(f"Successfully fetched: {url}")
                return response.text

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:  # Rate limited
                    wait_time = 2**attempt * 5
                    logger.warning(f"Rate limited, waiting {wait_time}s before retry")
                    await asyncio.sleep(wait_time)
                else:
                    logger.warning(f"HTTP error {e.response.status_code} for {url}")

            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")

            if attempt < self.max_retries - 1:
                await asyncio.sleep(2**attempt + random.uniform(0, 1))

        logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
        return None

    def parse(self, html: str) -> BeautifulSoup:
        """Parse HTML content."""
        return BeautifulSoup(html, "lxml")

    def extract_text_by_selectors(self, soup: BeautifulSoup, selectors: List[str]) -> Optional[str]:
        """Extract text using multiple selectors."""
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(strip=True)
                    if text:
                        return text
            except Exception as e:
                logger.debug(f"Selector '{selector}' failed: {e}")
        return None

    def extract_price_by_selectors(
        self, soup: BeautifulSoup, selectors: List[str]
    ) -> Optional[str]:
        """Extract price text using multiple selectors."""
        for selector in selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    if text and any(char.isdigit() for char in text):
                        return text
            except Exception as e:
                logger.debug(f"Price selector '{selector}' failed: {e}")
        return None

    def get_site_name(self, url: str) -> str:
        """Extract site name from URL."""
        try:
            return urlparse(url).netloc.replace("www.", "")
        except Exception:
            return "unknown"

    @abstractmethod
    async def extract_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract data from URL. Must be implemented by subclasses."""
        pass

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate extracted data."""
        required_fields = ["name", "price", "url"]
        return all(field in data and data[field] for field in required_fields)

    async def scrape(self, url: str) -> Optional[Dict[str, Any]]:
        """Main scraping method with normalization."""
        try:
            data = await self.extract_data(url)
            if not data or not self.validate_data(data):
                logger.warning(f"Invalid data extracted from {url}")
                return None

            # Normalize price to Naira
            if "price" in data and data["price"]:
                normalized_price = await currency_converter.normalize_price(str(data["price"]))
                if normalized_price:
                    data["price"] = float(normalized_price)
                    data["currency"] = "NGN"
                else:
                    logger.warning(f"Failed to normalize price for {url}")
                    return None

            logger.info(f"Successfully scraped data from {url}")
            return data

        except Exception as e:
            logger.error(f"Scraping failed for {url}: {e}")
            return None
