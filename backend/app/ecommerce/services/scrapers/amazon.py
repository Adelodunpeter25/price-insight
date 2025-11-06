"""Amazon-specific scraper implementation."""

from decimal import Decimal
from typing import Any, Dict, Optional

from loguru import logger

from app.ecommerce.services.scraper_base import BaseScraper
from app.utils.helpers import extract_price_from_text


class AmazonScraper(BaseScraper):
    """Amazon product scraper."""
    
    def __init__(self):
        """Initialize Amazon scraper."""
        super().__init__(timeout=30, max_retries=3)
    
    async def extract_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract product data from Amazon URL."""
        html = await self.fetch(url)
        if not html:
            return None
        
        soup = self.parse(html)
        
        try:
            # Extract product name
            name_selectors = [
                '#productTitle',
                '.product-title',
                'h1.a-size-large'
            ]
            name = None
            for selector in name_selectors:
                element = soup.select_one(selector)
                if element:
                    name = element.get_text(strip=True)
                    break
            
            if not name:
                logger.warning(f"Could not extract product name from {url}")
                return None
            
            # Extract price
            price_selectors = [
                '.a-price-whole',
                '.a-offscreen',
                '.a-price .a-offscreen',
                '#priceblock_dealprice',
                '#priceblock_ourprice'
            ]
            
            price = None
            for selector in price_selectors:
                element = soup.select_one(selector)
                if element:
                    price_text = element.get_text(strip=True)
                    price = extract_price_from_text(price_text)
                    if price:
                        break
            
            if not price:
                logger.warning(f"Could not extract price from {url}")
                return None
            
            # Extract availability
            availability_selectors = [
                '#availability span',
                '.a-color-success',
                '.a-color-state'
            ]
            
            availability = "Unknown"
            for selector in availability_selectors:
                element = soup.select_one(selector)
                if element:
                    availability = element.get_text(strip=True)
                    break
            
            return {
                'name': name,
                'price': price,
                'url': url,
                'availability': availability,
                'site': 'amazon',
                'currency': 'USD'  # Default, could be extracted
            }
            
        except Exception as e:
            logger.error(f"Error extracting data from Amazon URL {url}: {e}")
            return None