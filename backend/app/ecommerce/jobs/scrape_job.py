"""Scraping job for tracking product prices."""

from typing import Dict, List

from loguru import logger

from app.core.database import AsyncSessionLocal
from app.ecommerce.models import Product
from app.ecommerce.services.change_detector import ChangeDetector
from app.ecommerce.services.product_service import ProductService
from app.ecommerce.services.scrapers.amazon import AmazonScraper
from app.ecommerce.services.scrapers.generic import COMMON_SELECTORS, GenericScraper


async def scrape_tracked_products():
    """Main scraping job that processes all tracked products."""
    logger.info("Starting product scraping job")

    async with AsyncSessionLocal() as db:
        try:
            product_service = ProductService(db)
            change_detector = ChangeDetector(db)
            products = await product_service.get_products_to_track()

            if not products:
                logger.info("No products to track")
                return

            logger.info(f"Found {len(products)} products to scrape")

            # Group products by site for efficient scraping
            products_by_site = _group_products_by_site(products)

            total_scraped = 0
            total_deals = 0

            for site, site_products in products_by_site.items():
                logger.info(f"Scraping {len(site_products)} products from {site}")

                # Get appropriate scraper for site
                scraper = _get_scraper_for_site(site)

                async with scraper:
                    for product in site_products:
                        try:
                            # Scrape product data
                            data = await scraper.scrape(product.url)

                            if data and "price" in data:
                                # Process price change and trigger alerts
                                alerts = await change_detector.process_price_change(
                                    product.id,
                                    data["price"],
                                    data.get("currency", "USD"),
                                    data.get("availability"),
                                )

                                if alerts:
                                    total_deals += len(alerts)
                                    logger.info(
                                        f"Triggered {len(alerts)} alerts for {product.name}"
                                    )

                                total_scraped += 1

                            else:
                                logger.warning(f"Failed to scrape data for {product.name}")

                        except Exception as e:
                            logger.error(f"Error scraping product {product.id}: {e}")
                            continue

            logger.info(
                f"Scraping job completed: {total_scraped} products scraped, "
                f"{total_deals} alerts triggered"
            )

        except Exception as e:
            logger.error(f"Scraping job failed: {e}")
            raise


def _group_products_by_site(products: List[Product]) -> Dict[str, List[Product]]:
    """Group products by site for efficient scraping."""
    grouped = {}
    for product in products:
        site = product.site
        if site not in grouped:
            grouped[site] = []
        grouped[site].append(product)
    return grouped


def _get_scraper_for_site(site: str):
    """Get appropriate scraper for the given site."""
    if "amazon" in site.lower():
        return AmazonScraper()
    elif any(platform in site.lower() for platform in ["shopify", "woocommerce"]):
        # Use generic scraper with common selectors
        platform = "shopify" if "shopify" in site.lower() else "woocommerce"
        selectors = COMMON_SELECTORS.get(platform, COMMON_SELECTORS["shopify"])
        return GenericScraper(selectors)
    else:
        # Default to generic scraper with basic selectors
        default_selectors = {
            "name": ["h1", ".product-title", ".title", '[data-testid="product-title"]'],
            "price": [".price", ".cost", ".amount", '[data-testid="price"]'],
            "availability": [".stock", ".availability", ".in-stock"],
        }
        return GenericScraper(default_selectors)
