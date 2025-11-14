"""Property scraping job for real estate price tracking."""

from typing import Dict, List

import logging

logger = logging.getLogger(__name__)

from app.core.database import AsyncSessionLocal
from app.real_estate.models import Property
from app.real_estate.services.property_service import PropertyService
from app.real_estate.services.scrapers.property_scraper import PropertyScraper


async def scrape_tracked_properties():
    """Main property scraping job that processes all tracked properties."""
    logger.info("Starting property scraping job")

    async with AsyncSessionLocal() as db:
        try:
            property_service = PropertyService(db)
            properties = await property_service.get_properties_to_track()

            if not properties:
                logger.info("No properties to track")
                return

            logger.info(f"Found {len(properties)} properties to scrape")

            # Group properties by site for efficient scraping
            properties_by_site = _group_properties_by_site(properties)

            total_scraped = 0
            total_price_updates = 0

            for site, site_properties in properties_by_site.items():
                logger.info(f"Scraping {len(site_properties)} properties from {site}")

                # Use generic property scraper for all sites
                scraper = PropertyScraper()

                async with scraper:
                    for property_obj in site_properties:
                        try:
                            # Scrape property data
                            data = await scraper.scrape(property_obj.url)

                            if data and "price" in data:
                                # Update price history
                                await property_service.add_price_history(
                                    property_obj.id,
                                    data["price"],
                                    data.get("currency", "NGN"),
                                    data.get("price_per_sqm"),
                                    data.get("listing_status"),
                                )

                                total_price_updates += 1
                                logger.info(
                                    f"Updated price for {property_obj.name}: ₦{data['price']}"
                                )

                                total_scraped += 1

                            else:
                                logger.warning(f"Failed to scrape data for {property_obj.name}")

                        except Exception as e:
                            logger.error(f"Error scraping property {property_obj.id}: {e}")
                            continue

            logger.info(
                f"Property scraping job completed: {total_scraped} properties scraped, "
                f"{total_price_updates} price updates"
            )

        except Exception as e:
            logger.error(f"Property scraping job failed: {e}")
            raise


def _group_properties_by_site(properties: List[Property]) -> Dict[str, List[Property]]:
    """Group properties by site for efficient scraping."""
    grouped = {}
    for property_obj in properties:
        site = property_obj.site
        if site not in grouped:
            grouped[site] = []
        grouped[site].append(property_obj)
    return grouped
