"""Property watchlist API endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.cache import invalidate_cache
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.models.user import User
from app.real_estate.schemas.watchlist import (
    PropertyWatchlistCreate,
    PropertyWatchlistResponse,
    PropertyWatchlistUpdate,
)
from app.real_estate.services.watchlist_service import PropertyWatchlistService

router = APIRouter(prefix="/api/real-estate/watchlist", tags=["Real Estate Watchlist"])


@router.post("/", response_model=PropertyWatchlistResponse, status_code=201)
async def add_to_watchlist(
    data: PropertyWatchlistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add property to watchlist by name or URL."""
    try:
        watchlist = await PropertyWatchlistService.add_to_watchlist(
            db=db,
            user_id=current_user.id,
            property_name_or_url=data.property_name,
            target_price=data.target_price,
            alert_on_any_drop=data.alert_on_any_drop,
            alert_on_target=data.alert_on_target,
            notes=data.notes,
        )
        invalidate_cache("dashboard")
        return watchlist
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[PropertyWatchlistResponse])
def get_watchlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's watchlist."""
    return PropertyWatchlistService.get_user_watchlist(db, current_user.id)


@router.patch("/{watchlist_id}", response_model=PropertyWatchlistResponse)
def update_watchlist(
    watchlist_id: int,
    data: PropertyWatchlistUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update watchlist item."""
    try:
        updates = data.model_dump(exclude_unset=True)
        watchlist = PropertyWatchlistService.update_watchlist(
            db, watchlist_id, current_user.id, **updates
        )
        return watchlist
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{watchlist_id}", status_code=204)
def remove_from_watchlist(
    watchlist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove property from watchlist."""
    success = PropertyWatchlistService.remove_from_watchlist(db, watchlist_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    invalidate_cache("dashboard")
    return None
