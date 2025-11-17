"""Travel watchlist service."""

from typing import List, Optional, Union

from sqlalchemy.orm import Session

from app.travel.models.flight import Flight
from app.travel.models.hotel import Hotel
from app.travel.models.watchlist import TravelWatchlist
from app.travel.services.travel_search import TravelSearchService


class TravelWatchlistService:
    """Service for managing travel watchlists."""

    @staticmethod
    async def add_flight_to_watchlist(
        db: Session,
        user_id: int,
        flight_query_or_url: str,
        target_price: Optional[float] = None,
        alert_on_any_drop: bool = True,
        alert_on_target: bool = True,
        notes: Optional[str] = None,
    ) -> TravelWatchlist:
        """Add flight to watchlist by query or URL."""
        flight = None

        if TravelSearchService.validate_url(flight_query_or_url):
            flight = await TravelSearchService.scrape_flight_from_url(db, flight_query_or_url)
        else:
            tracked = TravelSearchService.search_tracked_flights(db, flight_query_or_url, 1)
            if tracked:
                flight = tracked[0]
            else:
                flights = await TravelSearchService.search_and_scrape_flights(
                    db, flight_query_or_url, 1
                )
                flight = flights[0] if flights else None

        if not flight:
            raise ValueError("Flight not found or could not be scraped")

        existing = (
            db.query(TravelWatchlist)
            .filter(
                TravelWatchlist.user_id == user_id,
                TravelWatchlist.flight_id == flight.id,
                TravelWatchlist.is_active == True,
            )
            .first()
        )

        if existing:
            return existing

        watchlist = TravelWatchlist(
            user_id=user_id,
            flight_id=flight.id,
            target_price=target_price,
            alert_on_any_drop=alert_on_any_drop,
            alert_on_target=alert_on_target,
            notes=notes,
        )

        db.add(watchlist)
        db.commit()
        db.refresh(watchlist)

        return watchlist

    @staticmethod
    async def add_hotel_to_watchlist(
        db: Session,
        user_id: int,
        hotel_query_or_url: str,
        target_price: Optional[float] = None,
        alert_on_any_drop: bool = True,
        alert_on_target: bool = True,
        notes: Optional[str] = None,
    ) -> TravelWatchlist:
        """Add hotel to watchlist by query or URL."""
        hotel = None

        if TravelSearchService.validate_url(hotel_query_or_url):
            hotel = await TravelSearchService.scrape_hotel_from_url(db, hotel_query_or_url)
        else:
            tracked = TravelSearchService.search_tracked_hotels(db, hotel_query_or_url, 1)
            if tracked:
                hotel = tracked[0]
            else:
                hotels = await TravelSearchService.search_and_scrape_hotels(
                    db, hotel_query_or_url, 1
                )
                hotel = hotels[0] if hotels else None

        if not hotel:
            raise ValueError("Hotel not found or could not be scraped")

        existing = (
            db.query(TravelWatchlist)
            .filter(
                TravelWatchlist.user_id == user_id,
                TravelWatchlist.hotel_id == hotel.id,
                TravelWatchlist.is_active == True,
            )
            .first()
        )

        if existing:
            return existing

        watchlist = TravelWatchlist(
            user_id=user_id,
            hotel_id=hotel.id,
            target_price=target_price,
            alert_on_any_drop=alert_on_any_drop,
            alert_on_target=alert_on_target,
            notes=notes,
        )

        db.add(watchlist)
        db.commit()
        db.refresh(watchlist)

        return watchlist

    @staticmethod
    def get_user_watchlist(db: Session, user_id: int) -> List[TravelWatchlist]:
        """Get all watchlist items for a user."""
        return (
            db.query(TravelWatchlist)
            .filter(TravelWatchlist.user_id == user_id, TravelWatchlist.is_active == True)
            .all()
        )

    @staticmethod
    def update_watchlist(
        db: Session, watchlist_id: int, user_id: int, **updates
    ) -> TravelWatchlist:
        """Update watchlist item."""
        watchlist = (
            db.query(TravelWatchlist)
            .filter(
                TravelWatchlist.id == watchlist_id,
                TravelWatchlist.user_id == user_id,
                TravelWatchlist.is_active == True,
            )
            .first()
        )

        if not watchlist:
            raise ValueError("Watchlist item not found")

        for key, value in updates.items():
            if hasattr(watchlist, key):
                setattr(watchlist, key, value)

        db.commit()
        db.refresh(watchlist)

        return watchlist

    @staticmethod
    def remove_from_watchlist(db: Session, watchlist_id: int, user_id: int) -> bool:
        """Remove item from watchlist."""
        watchlist = (
            db.query(TravelWatchlist)
            .filter(
                TravelWatchlist.id == watchlist_id,
                TravelWatchlist.user_id == user_id,
                TravelWatchlist.is_active == True,
            )
            .first()
        )

        if not watchlist:
            return False

        watchlist.is_active = False
        db.commit()

        return True