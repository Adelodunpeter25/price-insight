"""Utility scraping job for utilities and subscriptions price tracking."""

from typing import Dict, List

from loguru import logger

from app.core.database import AsyncSessionLocal
from app.utilities.models import UtilityService
from app.utilities.services.utility_service import UtilityServiceManager
from app.utilities.services.scrapers.utility_scraper import UtilityScraper


async def scrape_tracked_utilities():
    """Main utility scraping job that processes all tracked services."""
    logger.info("Starting utility scraping job")

    async with AsyncSessionLocal() as db:
        try:
            service_manager = UtilityServiceManager(db)
            services = await service_manager.get_services_to_track()

            if not services:
                logger.info("No utility services to track")
                return

            logger.info(f"Found {len(services)} utility services to scrape")

            # Group services by site for efficient scraping
            services_by_site = _group_services_by_site(services)

            total_scraped = 0
            total_price_updates = 0

            for site, site_services in services_by_site.items():
                logger.info(f"Scraping {len(site_services)} services from {site}")

                # Use generic utility scraper for all sites
                scraper = UtilityScraper()

                async with scraper:
                    for service in site_services:
                        try:
                            # Scrape service data
                            data = await scraper.scrape(service.url)

                            if data and "price" in data:
                                # Update price history
                                await service_manager.add_price_history(
                                    service.id,
                                    data["price"],
                                    data.get("currency", "NGN"),
                                    data.get("tariff_details"),
                                )

                                total_price_updates += 1
                                logger.info(f"Updated price for {service.name}: ₦{data['price']}")

                                total_scraped += 1

                            else:
                                logger.warning(f"Failed to scrape data for {service.name}")

                        except Exception as e:
                            logger.error(f"Error scraping service {service.id}: {e}")
                            continue

            logger.info(
                f"Utility scraping job completed: {total_scraped} services scraped, "
                f"{total_price_updates} price updates"
            )

        except Exception as e:
            logger.error(f"Utility scraping job failed: {e}")
            raise


def _group_services_by_site(services: List[UtilityService]) -> Dict[str, List[UtilityService]]:
    """Group services by site for efficient scraping."""
    grouped = {}
    for service in services:
        site = service.site
        if site not in grouped:
            grouped[site] = []
        grouped[site].append(service)
    return grouped
