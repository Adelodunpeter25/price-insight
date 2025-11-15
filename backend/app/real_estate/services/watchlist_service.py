"""Property watchlist service."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.real_estate.models.property import Property
from app.real_estate.models.watchlist import PropertyWatchlist
from app.real_estate.services.property_search import PropertySearchService


class PropertyWatchlistService:
    """Service for managing property watchlists."""

    @staticmethod
    async def add_to_watchlist(
        db: Session,
        user_id: int,
        property_name_or_url: str,
        target_price: Optional[float] = None,
        alert_on_any_drop: bool = True,
        alert_on_target: bool = True,
        notes: Optional[str] = None,
    ) -> PropertyWatchlist:
        """Add property to watchlist by name or URL."""
        property_obj = None

        if PropertySearchService.validate_url(property_name_or_url):
            property_obj = await PropertySearchService.scrape_property_from_url(
                db, property_name_or_url
            )
        else:
            tracked = PropertySearchService.search_tracked_properties(
                db, property_name_or_url, 1
            )
            if tracked:
                property_obj = tracked[0]
            else:
                properties = await PropertySearchService.search_and_scrape_properties(
                    db, property_name_or_url, 1
                )
                property_obj = properties[0] if properties else None

        if not property_obj:
            raise ValueError("Property not found or could not be scraped")

        existing = (
            db.query(PropertyWatchlist)
            .filter(
                PropertyWatchlist.user_id == user_id,
                PropertyWatchlist.property_id == property_obj.id,
                PropertyWatchlist.is_active == True,
            )
            .first()
        )

        if existing:
            return existing

        watchlist = PropertyWatchlist(
            user_id=user_id,
            property_id=property_obj.id,
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
    def get_user_watchlist(db: Session, user_id: int) -> List[PropertyWatchlist]:
        """Get all watchlist items for a user."""
        return (
            db.query(PropertyWatchlist)
            .filter(PropertyWatchlist.user_id == user_id, PropertyWatchlist.is_active == True)
            .all()
        )

    @staticmethod
    def update_watchlist(
        db: Session, watchlist_id: int, user_id: int, **updates
    ) -> PropertyWatchlist:
        """Update watchlist item."""
        watchlist = (
            db.query(PropertyWatchlist)
            .filter(
                PropertyWatchlist.id == watchlist_id,
                PropertyWatchlist.user_id == user_id,
                PropertyWatchlist.is_active == True,
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
        """Remove property from watchlist."""
        watchlist = (
            db.query(PropertyWatchlist)
            .filter(
                PropertyWatchlist.id == watchlist_id,
                PropertyWatchlist.user_id == user_id,
                PropertyWatchlist.is_active == True,
            )
            .first()
        )

        if not watchlist:
            return False

        watchlist.is_active = False
        db.commit()

        return True
