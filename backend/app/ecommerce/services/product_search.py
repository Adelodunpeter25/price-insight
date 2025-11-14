"""Product search and discovery service."""

import logging
from typing import List, Optional
from urllib.parse import urlparse

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.scraping.scraper_factory import scraper_factory
from app.ecommerce.models.product import Product
from app.utils.helpers import validate_url

logger = logging.getLogger(__name__)


class ProductSearchService:
    """Service for searching and discovering products."""

    @staticmethod
    def search_tracked_products(db: Session, query: str, limit: int = 10) -> List[Product]:
        """Search existing tracked products by name."""
        try:
            search_term = f"%{query}%"
            products = db.query(Product).filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.url.ilike(search_term)
                )
            ).limit(limit).all()
            
            return products
            
        except Exception as e:
            logger.error(f"Error searching tracked products: {e}")
            return []

    @staticmethod
    async def scrape_product_from_url(db: Session, url: str) -> Optional[Product]:
        """Scrape product from URL and add to database."""
        try:
            if not validate_url(url):
                logger.error(f"Invalid URL: {url}")
                return None
            
            # Check if product already exists
            existing = db.query(Product).filter(Product.url == url).first()
            if existing:
                return existing
            
            # Get appropriate scraper
            scraper = scraper_factory.get_scraper(url, category="ecommerce")
            if not scraper:
                logger.error(f"No scraper available for URL: {url}")
                return None
            
            # Scrape product data
            async with scraper:
                product_data = await scraper.scrape(url)
            
            if not product_data:
                logger.error(f"Failed to scrape product from URL: {url}")
                return None
            
            # Create product
            product = Product(
                name=product_data["name"],
                url=product_data["url"],
                site=product_data["site"],
                is_tracked=True
            )
            
            db.add(product)
            db.commit()
            db.refresh(product)
            
            # Add initial price history
            from app.ecommerce.models.price_history import PriceHistory
            from decimal import Decimal
            
            price_history = PriceHistory(
                product_id=product.id,
                price=Decimal(str(product_data["price"])),
                currency=product_data.get("currency", "NGN"),
                availability=product_data.get("availability", "Unknown"),
                source="scraper"
            )
            
            db.add(price_history)
            db.commit()
            
            logger.info(f"Successfully scraped and added product: {product.name}")
            return product
            
        except Exception as e:
            logger.error(f"Error scraping product from URL: {e}")
            db.rollback()
            return None

    @staticmethod
    async def search_and_scrape_products(db: Session, product_name: str, max_results: int = 5) -> List[Product]:
        """Search for products across multiple e-commerce sites."""
        try:
            # Common Nigerian e-commerce sites
            search_urls = [
                f"https://www.jumia.com.ng/catalog/?q={product_name.replace(' ', '+')}",
                f"https://www.konga.com/search?search={product_name.replace(' ', '+')}",
                f"https://www.amazon.com/s?k={product_name.replace(' ', '+')}",
            ]
            
            products = []
            
            for search_url in search_urls:
                try:
                    scraper = scraper_factory.get_scraper(search_url, category="ecommerce")
                    if not scraper:
                        continue
                    
                    async with scraper:
                        # Fetch search results page
                        html = await scraper.fetch(search_url)
                        if not html:
                            continue
                        
                        soup = scraper.parse(html)
                        
                        # Extract product links (site-specific selectors)
                        product_links = ProductSearchService._extract_product_links(soup, search_url)
                        
                        # Scrape first few products
                        for link in product_links[:max_results]:
                            product = await ProductSearchService.scrape_product_from_url(db, link)
                            if product:
                                products.append(product)
                            
                            if len(products) >= max_results:
                                break
                    
                    if len(products) >= max_results:
                        break
                        
                except Exception as e:
                    logger.error(f"Error searching on {search_url}: {e}")
                    continue
            
            return products
            
        except Exception as e:
            logger.error(f"Error in search and scrape: {e}")
            return []

    @staticmethod
    def _extract_product_links(soup, base_url: str) -> List[str]:
        """Extract product links from search results page."""
        links = []
        domain = urlparse(base_url).netloc
        
        try:
            if "jumia" in domain:
                # Jumia product links
                for link in soup.select('a.core'):
                    href = link.get('href')
                    if href and '/product/' in href:
                        full_url = f"https://www.jumia.com.ng{href}" if href.startswith('/') else href
                        links.append(full_url)
                        
            elif "konga" in domain:
                # Konga product links
                for link in soup.select('a[href*="/product/"]'):
                    href = link.get('href')
                    if href:
                        full_url = f"https://www.konga.com{href}" if href.startswith('/') else href
                        links.append(full_url)
                        
            elif "amazon" in domain:
                # Amazon product links
                for link in soup.select('a[href*="/dp/"]'):
                    href = link.get('href')
                    if href and '/dp/' in href:
                        full_url = f"https://www.amazon.com{href}" if href.startswith('/') else href
                        links.append(full_url)
            
        except Exception as e:
            logger.error(f"Error extracting product links: {e}")
        
        return links[:10]  # Limit to 10 links per site
