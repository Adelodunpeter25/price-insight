"""Enhanced base scraper with rate limiting and error handling."""

import asyncio
import logging
import random
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

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
        
        # Common selectors for major e-commerce sites
        self.common_selectors = {
            'name': [
                '#productTitle', '.product-title', '.product__title', '.product_title',
                'h1.product-single__title', '.entry-title', '[data-testid="product-title"]',
                '.pdp-product-name', '.product-name', '.item-title'
            ],
            'price': [
                '.a-price-whole', '.a-offscreen', '.a-price .a-offscreen', '#priceblock_dealprice',
                '#priceblock_ourprice', '.price', '.product-price', '.money', '.product__price',
                '.woocommerce-Price-amount', '.amount', '[data-testid="price"]',
                '.current-price', '.sale-price', '.price-current'
            ],
            'availability': [
                '#availability span', '.a-color-success', '.a-color-state',
                '.stock-status', '.availability', '.stock', '.in-stock'
            ]
        }

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

    def _get_headers(self, url: str = None) -> Dict[str, str]:
        """Get randomized headers with site-specific adjustments."""
        headers = {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        
        # Site-specific headers
        if url:
            domain = urlparse(url).netloc.lower()
            if 'amazon' in domain:
                headers.update({
                    "Accept-Language": "en-US,en;q=0.9",
                    "sec-fetch-dest": "document",
                    "sec-fetch-mode": "navigate",
                    "sec-fetch-site": "none"
                })
            elif 'jumia' in domain:
                headers["Accept-Language"] = "en-NG,en;q=0.9"
                
        return headers

    def normalize_url(self, url: str) -> str:
        """Normalize URL by removing tracking parameters."""
        try:
            parsed = urlparse(url)
            parsed = parsed._replace(fragment='')
            
            query_params = parse_qs(parsed.query)
            essential_params = {}
            
            domain = parsed.netloc.lower()
            if 'amazon' in domain:
                for key in ['dp', 'gp', 'asin', 'th', 'psc']:
                    if key in query_params:
                        essential_params[key] = query_params[key]
            elif 'jumia' in domain:
                for key in ['sku', 'catalog']:
                    if key in query_params:
                        essential_params[key] = query_params[key]
            elif 'konga' in domain:
                for key in ['product_id', 'pid']:
                    if key in query_params:
                        essential_params[key] = query_params[key]
            
            clean_query = urlencode(essential_params, doseq=True) if essential_params else ''
            return urlunparse(parsed._replace(query=clean_query))
        except Exception:
            return url

    async def fetch(self, url: str) -> Optional[str]:
        """Fetch HTML content with rate limiting and retry logic."""
        normalized_url = self.normalize_url(url)
        
        if not validate_url(normalized_url):
            logger.error(f"Invalid URL: {normalized_url}")
            return None

        for attempt in range(self.max_retries):
            try:
                await asyncio.sleep(self.rate_limit + random.uniform(0, 0.5))

                response = await self.session.get(normalized_url, headers=self._get_headers(normalized_url))
                response.raise_for_status()

                logger.info(f"Successfully fetched: {normalized_url}")
                return response.text

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    wait_time = 2**attempt * 5
                    logger.warning(f"Rate limited, waiting {wait_time}s before retry")
                    await asyncio.sleep(wait_time)
                elif e.response.status_code == 403:
                    logger.warning(f"Access forbidden for {normalized_url}, trying with different headers")
                    # Rotate user agent
                    self.user_agents = self.user_agents[1:] + [self.user_agents[0]]
                else:
                    logger.warning(f"HTTP error {e.response.status_code} for {normalized_url}")

            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {normalized_url}: {e}")

            if attempt < self.max_retries - 1:
                await asyncio.sleep(2**attempt + random.uniform(0, 1))

        logger.error(f"Failed to fetch {normalized_url} after {self.max_retries} attempts")
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
                    # Look for price patterns
                    if text and re.search(r'[₦$£€¥]?[\d,]+\.?\d*', text):
                        return text
            except Exception as e:
                logger.debug(f"Price selector '{selector}' failed: {e}")
        return None

    def smart_extract_data(self, soup: BeautifulSoup, url: str) -> Optional[Dict[str, Any]]:
        """Smart extraction using common selectors and fallbacks."""
        try:
            # Extract name
            name = self.extract_text_by_selectors(soup, self.common_selectors['name'])
            if not name:
                # Fallback to title tag or h1
                title_elem = soup.find('title')
                if title_elem:
                    name = title_elem.get_text(strip=True)
                else:
                    h1_elem = soup.find('h1')
                    if h1_elem:
                        name = h1_elem.get_text(strip=True)
            
            if not name:
                return None

            # Extract price
            price_text = self.extract_price_by_selectors(soup, self.common_selectors['price'])
            if not price_text:
                # Fallback: search for price patterns in text
                all_text = soup.get_text()
                price_match = re.search(r'[₦$£€¥]([\d,]+(?:\.\d{2})?)', all_text)
                if price_match:
                    price_text = price_match.group(0)
            
            if not price_text:
                return None

            # Extract availability
            availability = self.extract_text_by_selectors(soup, self.common_selectors['availability']) or "Unknown"

            return {
                "name": name[:200],  # Limit name length
                "price": price_text,
                "url": url,
                "availability": availability,
                "site": self.get_site_name(url),
                "currency": "NGN",
            }

        except Exception as e:
            logger.error(f"Smart extraction failed for {url}: {e}")
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
