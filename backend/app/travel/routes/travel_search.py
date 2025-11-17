"""Travel search API endpoints."""

from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_database_session
from app.travel.services.travel_search import TravelSearchService

router = APIRouter(prefix="/api/travel/search", tags=["Travel Search"])


@router.get("/flights/tracked")
async def search_tracked_flights(
    q: str = Query(..., description="Search query for flights"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    db: Session = Depends(get_database_session)
):
    """Search existing tracked flights."""
    flights = TravelSearchService.search_tracked_flights(db, q, limit)
    
    return {
        "query": q,
        "count": len(flights),
        "flights": [
            {
                "id": flight.id,
                "origin": flight.origin,
                "destination": flight.destination,
                "airline": flight.airline,
                "price": float(flight.price),
                "url": flight.url,
                "site": flight.site,
                "flight_class": flight.flight_class,
                "passengers": flight.passengers,
            }
            for flight in flights
        ]
    }


@router.get("/hotels/tracked")
async def search_tracked_hotels(
    q: str = Query(..., description="Search query for hotels"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    db: Session = Depends(get_database_session)
):
    """Search existing tracked hotels."""
    hotels = TravelSearchService.search_tracked_hotels(db, q, limit)
    
    return {
        "query": q,
        "count": len(hotels),
        "hotels": [
            {
                "id": hotel.id,
                "name": hotel.name,
                "location": hotel.location,
                "price_per_night": float(hotel.price_per_night),
                "total_price": float(hotel.total_price),
                "rating": float(hotel.rating) if hotel.rating else None,
                "url": hotel.url,
                "site": hotel.site,
                "room_type": hotel.room_type,
                "guests": hotel.guests,
            }
            for hotel in hotels
        ]
    }


@router.post("/flights/scrape")
async def scrape_flight_from_url(
    url: str = Query(..., description="Flight URL to scrape"),
    db: Session = Depends(get_database_session)
):
    """Scrape flight from URL and add to database."""
    if not TravelSearchService.validate_url(url):
        return {"error": "Invalid URL provided"}
    
    flight = await TravelSearchService.scrape_flight_from_url(db, url)
    
    if not flight:
        return {"error": "Failed to scrape flight from URL"}
    
    return {
        "message": "Flight scraped successfully",
        "flight": {
            "id": flight.id,
            "origin": flight.origin,
            "destination": flight.destination,
            "airline": flight.airline,
            "price": float(flight.price),
            "url": flight.url,
            "site": flight.site,
            "flight_class": flight.flight_class,
            "passengers": flight.passengers,
        }
    }


@router.post("/hotels/scrape")
async def scrape_hotel_from_url(
    url: str = Query(..., description="Hotel URL to scrape"),
    db: Session = Depends(get_database_session)
):
    """Scrape hotel from URL and add to database."""
    if not TravelSearchService.validate_url(url):
        return {"error": "Invalid URL provided"}
    
    hotel = await TravelSearchService.scrape_hotel_from_url(db, url)
    
    if not hotel:
        return {"error": "Failed to scrape hotel from URL"}
    
    return {
        "message": "Hotel scraped successfully",
        "hotel": {
            "id": hotel.id,
            "name": hotel.name,
            "location": hotel.location,
            "price_per_night": float(hotel.price_per_night),
            "total_price": float(hotel.total_price),
            "rating": float(hotel.rating) if hotel.rating else None,
            "url": hotel.url,
            "site": hotel.site,
            "room_type": hotel.room_type,
            "guests": hotel.guests,
        }
    }


@router.get("/flights/discover")
async def discover_flights(
    route: str = Query(..., description="Flight route (e.g., 'Lagos to London' or 'LOS-LHR')"),
    max_results: int = Query(5, ge=1, le=10, description="Maximum number of results"),
    db: Session = Depends(get_database_session)
):
    """Search and scrape flights from multiple travel sites."""
    flights = await TravelSearchService.search_and_scrape_flights(db, route, max_results)
    
    return {
        "route": route,
        "count": len(flights),
        "flights": [
            {
                "id": flight.id,
                "origin": flight.origin,
                "destination": flight.destination,
                "airline": flight.airline,
                "price": float(flight.price),
                "url": flight.url,
                "site": flight.site,
                "flight_class": flight.flight_class,
                "passengers": flight.passengers,
            }
            for flight in flights
        ]
    }


@router.get("/hotels/discover")
async def discover_hotels(
    destination: str = Query(..., description="Hotel destination (e.g., 'Lagos', 'London')"),
    max_results: int = Query(5, ge=1, le=10, description="Maximum number of results"),
    db: Session = Depends(get_database_session)
):
    """Search and scrape hotels from multiple travel sites."""
    hotels = await TravelSearchService.search_and_scrape_hotels(db, destination, max_results)
    
    return {
        "destination": destination,
        "count": len(hotels),
        "hotels": [
            {
                "id": hotel.id,
                "name": hotel.name,
                "location": hotel.location,
                "price_per_night": float(hotel.price_per_night),
                "total_price": float(hotel.total_price),
                "rating": float(hotel.rating) if hotel.rating else None,
                "url": hotel.url,
                "site": hotel.site,
                "room_type": hotel.room_type,
                "guests": hotel.guests,
            }
            for hotel in hotels
        ]
    }