"""Travel search and discovery service."""

import re
from typing import Dict, List, Optional, Union
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.core.scraping.scraper_factory import scraper_factory
from app.travel.models.flight import Flight
from app.travel.models.hotel import Hotel
from app.travel.models.price_history import TravelPriceHistory


class TravelSearchService:
    """Service for searching and discovering flights and hotels."""

    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate if string is a URL."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    @staticmethod
    def search_tracked_flights(
        db: Session, query: str, limit: int = 10
    ) -> List[Flight]:
        """Search existing tracked flights."""
        # Search by origin-destination or airline
        return (
            db.query(Flight)
            .filter(
                db.or_(
                    Flight.origin.ilike(f"%{query}%"),
                    Flight.destination.ilike(f"%{query}%"),
                    Flight.airline.ilike(f"%{query}%"),
                ),
                Flight.is_active == True
            )
            .limit(limit)
            .all()
        )

    @staticmethod
    def search_tracked_hotels(
        db: Session, query: str, limit: int = 10
    ) -> List[Hotel]:
        """Search existing tracked hotels."""
        return (
            db.query(Hotel)
            .filter(
                db.or_(
                    Hotel.name.ilike(f"%{query}%"),
                    Hotel.location.ilike(f"%{query}%"),
                ),
                Hotel.is_active == True
            )
            .limit(limit)
            .all()
        )

    @staticmethod
    async def scrape_flight_from_url(db: Session, url: str) -> Optional[Flight]:
        """Scrape flight from URL and add to database."""
        existing = db.query(Flight).filter(Flight.url == url).first()
        if existing:
            return existing

        scraper = scraper_factory.get_scraper(url, "travel")
        if not scraper:
            return None

        async with scraper:
            flight_data = await scraper.scrape(url)

        if not flight_data or flight_data.get("type") != "flight":
            return None

        flight = Flight(
            origin=flight_data.get("origin", "")[:10],
            destination=flight_data.get("destination", "")[:10],
            departure_date=flight_data.get("departure_date"),
            return_date=flight_data.get("return_date"),
            airline=flight_data.get("airline", "")[:100],
            flight_class=flight_data.get("flight_class", "economy"),
            price=flight_data.get("price", 0),
            currency=flight_data.get("currency", "NGN"),
            url=url,
            site=flight_data.get("site", ""),
            passengers=flight_data.get("passengers", 1),
            is_tracked=1,
        )

        db.add(flight)
        db.flush()

        price_history = TravelPriceHistory(
            flight_id=flight.id,
            price=flight_data.get("price", 0),
            currency=flight_data.get("currency", "NGN"),
            source="scraper",
        )

        db.add(price_history)
        db.commit()
        db.refresh(flight)

        return flight

    @staticmethod
    async def scrape_hotel_from_url(db: Session, url: str) -> Optional[Hotel]:
        """Scrape hotel from URL and add to database."""
        existing = db.query(Hotel).filter(Hotel.url == url).first()
        if existing:
            return existing

        scraper = scraper_factory.get_scraper(url, "travel")
        if not scraper:
            return None

        async with scraper:
            hotel_data = await scraper.scrape(url)

        if not hotel_data or hotel_data.get("type") != "hotel":
            return None

        hotel = Hotel(
            name=hotel_data.get("name", "")[:200],
            location=hotel_data.get("location", "")[:200],
            check_in=hotel_data.get("check_in"),
            check_out=hotel_data.get("check_out"),
            room_type=hotel_data.get("room_type", "standard"),
            price_per_night=hotel_data.get("price_per_night", 0),
            total_price=hotel_data.get("total_price", 0),
            currency=hotel_data.get("currency", "NGN"),
            url=url,
            site=hotel_data.get("site", ""),
            guests=hotel_data.get("guests", 2),
            rating=hotel_data.get("rating"),
            is_tracked=1,
        )

        db.add(hotel)
        db.flush()

        price_history = TravelPriceHistory(
            hotel_id=hotel.id,
            price=hotel_data.get("total_price", 0),
            currency=hotel_data.get("currency", "NGN"),
            source="scraper",
        )

        db.add(price_history)
        db.commit()
        db.refresh(hotel)

        return hotel

    @staticmethod
    async def search_and_scrape_flights(
        db: Session, route: str, max_results: int = 5
    ) -> List[Flight]:
        """Search and scrape flights from multiple sites."""
        # Parse route (e.g., "Lagos to London" or "LOS-LHR")
        route_parts = route.replace(" to ", "-").replace(" ", "+")
        
        search_urls = [
            f"https://www.kayak.com/flights/{route_parts}",
            f"https://www.expedia.com/Flights-Search?trip=oneway&leg1=from:{route_parts}",
            f"https://www.booking.com/flights/search.html?ss={route_parts}",
        ]

        flights = []

        for search_url in search_urls:
            if len(flights) >= max_results:
                break

            try:
                scraper = scraper_factory.get_scraper(search_url, "travel")
                if not scraper:
                    continue

                async with scraper:
                    html = await scraper.fetch(search_url)

                if not html:
                    continue

                soup = BeautifulSoup(html, "html.parser")
                flight_links = TravelSearchService._extract_flight_links(soup, search_url)

                for link in flight_links[: max_results - len(flights)]:
                    flight = await TravelSearchService.scrape_flight_from_url(db, link)
                    if flight:
                        flights.append(flight)

            except Exception:
                continue

        return flights

    @staticmethod
    async def search_and_scrape_hotels(
        db: Session, destination: str, max_results: int = 5
    ) -> List[Hotel]:
        """Search and scrape hotels from multiple sites."""
        destination_encoded = destination.replace(" ", "+")
        
        search_urls = [
            f"https://www.booking.com/searchresults.html?ss={destination_encoded}",
            f"https://www.hotels.com/search.do?q-destination={destination_encoded}",
            f"https://www.expedia.com/Hotels-Search?destination={destination_encoded}",
        ]

        hotels = []

        for search_url in search_urls:
            if len(hotels) >= max_results:
                break

            try:
                scraper = scraper_factory.get_scraper(search_url, "travel")
                if not scraper:
                    continue

                async with scraper:
                    html = await scraper.fetch(search_url)

                if not html:
                    continue

                soup = BeautifulSoup(html, "html.parser")
                hotel_links = TravelSearchService._extract_hotel_links(soup, search_url)

                for link in hotel_links[: max_results - len(hotels)]:
                    hotel = await TravelSearchService.scrape_hotel_from_url(db, link)
                    if hotel:
                        hotels.append(hotel)

            except Exception:
                continue

        return hotels

    @staticmethod
    def _extract_flight_links(soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract flight links from search results."""
        links = []
        domain = urlparse(base_url).netloc

        if "kayak" in domain:
            for link in soup.select('a[href*="/flights/"]'):
                href = link.get("href")
                if href and "/flights/" in href:
                    full_url = href if href.startswith("http") else f"https://{domain}{href}"
                    links.append(full_url)

        elif "expedia" in domain:
            for link in soup.select('a[href*="/Flight-Information"]'):
                href = link.get("href")
                if href:
                    full_url = href if href.startswith("http") else f"https://{domain}{href}"
                    links.append(full_url)

        elif "booking" in domain:
            for link in soup.select('a[href*="/flights/"]'):
                href = link.get("href")
                if href and "/flights/" in href:
                    full_url = href if href.startswith("http") else f"https://{domain}{href}"
                    links.append(full_url)

        return list(set(links))

    @staticmethod
    def _extract_hotel_links(soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract hotel links from search results."""
        links = []
        domain = urlparse(base_url).netloc

        if "booking" in domain:
            for link in soup.select('a[href*="/hotel/"]'):
                href = link.get("href")
                if href and "/hotel/" in href:
                    full_url = href if href.startswith("http") else f"https://{domain}{href}"
                    links.append(full_url)

        elif "hotels" in domain:
            for link in soup.select('a[href*="/ho"]'):
                href = link.get("href")
                if href and "/ho" in href:
                    full_url = href if href.startswith("http") else f"https://{domain}{href}"
                    links.append(full_url)

        elif "expedia" in domain:
            for link in soup.select('a[href*="/Hotel-Information"]'):
                href = link.get("href")
                if href:
                    full_url = href if href.startswith("http") else f"https://{domain}{href}"
                    links.append(full_url)

        return list(set(links))