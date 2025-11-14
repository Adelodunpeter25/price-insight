#!/usr/bin/env python3
"""CLI tool for testing scraping functionality."""

import asyncio
import sys
from typing import List

from app.core.scraping.scraper_factory import scraper_factory
from app.core.scraping.scraper_manager import scraper_manager


async def test_single_url(url: str, category: str = "auto"):
    """Test scraping a single URL."""
    print(f"Testing URL: {url}")
    print(f"Category: {category}")
    print("-" * 50)
    
    try:
        result = await scraper_manager.scrape_url(url, category)
        if result:
            print("✅ Scraping successful!")
            print(f"Name: {result.get('name', 'N/A')}")
            print(f"Price: {result.get('price', 'N/A')} {result.get('currency', 'NGN')}")
            print(f"Site: {result.get('site', 'N/A')}")
            if 'availability' in result:
                print(f"Availability: {result['availability']}")
            if 'location' in result:
                print(f"Location: {result['location']}")
            print(f"URL: {result.get('url', 'N/A')}")
        else:
            print("❌ Scraping failed - no data extracted")
    except Exception as e:
        print(f"❌ Scraping failed with error: {e}")


async def test_multiple_urls(urls: List[str], category: str = "auto"):
    """Test scraping multiple URLs."""
    print(f"Testing {len(urls)} URLs")
    print(f"Category: {category}")
    print("-" * 50)
    
    try:
        results = await scraper_manager.scrape_multiple(urls, category)
        print(f"✅ Scraped {len(results)} out of {len(urls)} URLs successfully")
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.get('name', 'Unknown')}")
            print(f"   Price: {result.get('price', 'N/A')} {result.get('currency', 'NGN')}")
            print(f"   Site: {result.get('site', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Batch scraping failed with error: {e}")


def show_supported_sites():
    """Show supported sites."""
    factory = scraper_factory
    
    print("🛒 E-commerce Sites:")
    for site in factory.ecommerce_sites.keys():
        print(f"  - {site}")
    
    print("\n✈️ Travel Sites:")
    for site in factory.travel_sites.keys():
        print(f"  - {site}")
    
    print("\n🏠 Real Estate Sites:")
    for site in factory.real_estate_sites.keys():
        print(f"  - {site}")
    
    print("\n⚡ Utility Sites:")
    for site in factory.utility_sites.keys():
        print(f"  - {site}")
    
    print("\n📝 Note: Generic scraping is available for other sites")


async def main():
    """Main CLI function."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python test_scraper.py <url> [category]")
        print("  python test_scraper.py --sites")
        print("  python test_scraper.py --test-batch")
        print("\nCategories: auto, ecommerce, travel, real_estate, utilities")
        return
    
    command = sys.argv[1]
    
    if command == "--sites":
        show_supported_sites()
        return
    
    if command == "--test-batch":
        # Test URLs for different categories
        test_urls = [
            "https://www.amazon.com/dp/B08N5WRWNW",  # Amazon product
            "https://www.booking.com/hotel/us/example.html",  # Hotel
            "https://www.jumia.com.ng/generic-product.html",  # Jumia product
        ]
        await test_multiple_urls(test_urls)
        return
    
    # Single URL test
    url = command
    category = sys.argv[2] if len(sys.argv) > 2 else "auto"
    
    await test_single_url(url, category)


if __name__ == "__main__":
    asyncio.run(main())