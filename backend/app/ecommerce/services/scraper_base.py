"""Abstract base class for web scrapers."""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import httpx
from bs4 import BeautifulSoup
from loguru import logger

from app.utils.currency import currency_converter
from app.utils.helpers import validate_url


class BaseScraper(ABC):
    """Abstract base scraper class."""

    def __init__(self, timeout: int = 30, max_retries: int = 3):
        """Initialize scraper."""
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = None
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        ]

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = httpx.AsyncClient(
            timeout=self.timeout,
            headers={"User-Agent": self.user_agents[0]},
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.aclose()

    async def fetch(self, url: str) -> Optional[str]:
        """Fetch HTML content from URL with retry logic."""
        if not validate_url(url):
            logger.error(f"Invalid URL: {url}")
            return None

        for attempt in range(self.max_retries):
            try:
                await asyncio.sleep(1)  # Rate limiting
                response = await self.session.get(url)
                response.raise_for_status()
                logger.info(f"Successfully fetched: {url}")
                return response.text
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2**attempt)  # Exponential backoff

        logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
        return None

    def parse(self, html: str) -> BeautifulSoup:
        """Parse HTML content."""
        return BeautifulSoup(html, "lxml")

    @abstractmethod
    async def extract_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract product data from URL. Must be implemented by subclasses."""
        pass

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate extracted data."""
        required_fields = ["name", "price", "url"]
        return all(field in data and data[field] for field in required_fields)

    async def scrape(self, url: str) -> Optional[Dict[str, Any]]:
        """Main scraping method."""
        try:
            data = await self.extract_data(url)
            if data and self.validate_data(data):
                # Normalize price to Naira
                if "price" in data and data["price"]:
                    normalized_price = await currency_converter.normalize_price(str(data["price"]))
                    if normalized_price:
                        data["price"] = float(normalized_price)
                        data["currency"] = "NGN"
                
                logger.info(f"Successfully scraped data from {url}")
                return data
            else:
                logger.warning(f"Invalid data extracted from {url}")
                return None
        except Exception as e:
            logger.error(f"Scraping failed for {url}: {e}")
            return None
