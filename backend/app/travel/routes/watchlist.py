"""Travel watchlist API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_database_session
from app.core.models.user import User
from app.travel.services.watchlist_service import TravelWatchlistService

router = APIRouter(prefix="/api/travel/watchlist", tags=["Travel Watchlist"])


class AddFlightToWatchlistRequest(BaseModel):
    """Request model for adding flight to watchlist."""
    flight_query_or_url: str
    target_price: Optional[float] = None
    alert_on_any_drop: bool = True
    alert_on_target: bool = True
    notes: Optional[str] = None


class AddHotelToWatchlistRequest(BaseModel):
    """Request model for adding hotel to watchlist."""
    hotel_query_or_url: str
    target_price: Optional[float] = None
    alert_on_any_drop: bool = True
    alert_on_target: bool = True
    notes: Optional[str] = None


class UpdateWatchlistRequest(BaseModel):
    """Request model for updating watchlist item."""
    target_price: Optional[float] = None
    alert_on_any_drop: Optional[bool] = None
    alert_on_target: Optional[bool] = None
    notes: Optional[str] = None


@router.post("/flights", status_code=201)
async def add_flight_to_watchlist(
    request: AddFlightToWatchlistRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """Add flight to watchlist by query or URL."""
    try:
        watchlist = await TravelWatchlistService.add_flight_to_watchlist(
            db=db,
            user_id=current_user.id,
            flight_query_or_url=request.flight_query_or_url,
            target_price=request.target_price,
            alert_on_any_drop=request.alert_on_any_drop,
            alert_on_target=request.alert_on_target,
            notes=request.notes,
        )
        return {
            "id": watchlist.id,
            "flight_id": watchlist.flight_id,
            "target_price": float(watchlist.target_price) if watchlist.target_price else None,
            "alert_on_any_drop": watchlist.alert_on_any_drop,
            "alert_on_target": watchlist.alert_on_target,
            "notes": watchlist.notes,
            "created_at": watchlist.created_at,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/hotels", status_code=201)
async def add_hotel_to_watchlist(
    request: AddHotelToWatchlistRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """Add hotel to watchlist by query or URL."""
    try:
        watchlist = await TravelWatchlistService.add_hotel_to_watchlist(
            db=db,
            user_id=current_user.id,
            hotel_query_or_url=request.hotel_query_or_url,
            target_price=request.target_price,
            alert_on_any_drop=request.alert_on_any_drop,
            alert_on_target=request.alert_on_target,
            notes=request.notes,
        )
        return {
            "id": watchlist.id,
            "hotel_id": watchlist.hotel_id,
            "target_price": float(watchlist.target_price) if watchlist.target_price else None,
            "alert_on_any_drop": watchlist.alert_on_any_drop,
            "alert_on_target": watchlist.alert_on_target,
            "notes": watchlist.notes,
            "created_at": watchlist.created_at,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("")
async def get_user_watchlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """Get all watchlist items for current user."""
    watchlist_items = TravelWatchlistService.get_user_watchlist(db, current_user.id)
    
    items = []
    for item in watchlist_items:
        item_data = {
            "id": item.id,
            "target_price": float(item.target_price) if item.target_price else None,
            "alert_on_any_drop": item.alert_on_any_drop,
            "alert_on_target": item.alert_on_target,
            "notes": item.notes,
            "created_at": item.created_at,
        }
        
        if item.flight_id:
            item_data.update({
                "type": "flight",
                "flight_id": item.flight_id,
                "flight": {
                    "id": item.flight.id,
                    "origin": item.flight.origin,
                    "destination": item.flight.destination,
                    "airline": item.flight.airline,
                    "price": float(item.flight.price),
                    "url": item.flight.url,
                    "site": item.flight.site,
                }
            })
        elif item.hotel_id:
            item_data.update({
                "type": "hotel",
                "hotel_id": item.hotel_id,
                "hotel": {
                    "id": item.hotel.id,
                    "name": item.hotel.name,
                    "location": item.hotel.location,
                    "price_per_night": float(item.hotel.price_per_night),
                    "total_price": float(item.hotel.total_price),
                    "rating": float(item.hotel.rating) if item.hotel.rating else None,
                    "url": item.hotel.url,
                    "site": item.hotel.site,
                }
            })
        
        items.append(item_data)
    
    return {
        "items": items,
        "total": len(items)
    }


@router.get("/{watchlist_id}")
async def get_watchlist_item(
    watchlist_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """Get specific watchlist item."""
    watchlist_items = TravelWatchlistService.get_user_watchlist(db, current_user.id)
    item = next((w for w in watchlist_items if w.id == watchlist_id), None)
    
    if not item:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    
    item_data = {
        "id": item.id,
        "target_price": float(item.target_price) if item.target_price else None,
        "alert_on_any_drop": item.alert_on_any_drop,
        "alert_on_target": item.alert_on_target,
        "notes": item.notes,
        "created_at": item.created_at,
    }
    
    if item.flight_id:
        item_data.update({
            "type": "flight",
            "flight_id": item.flight_id,
            "flight": {
                "id": item.flight.id,
                "origin": item.flight.origin,
                "destination": item.flight.destination,
                "airline": item.flight.airline,
                "price": float(item.flight.price),
                "url": item.flight.url,
                "site": item.flight.site,
            }
        })
    elif item.hotel_id:
        item_data.update({
            "type": "hotel",
            "hotel_id": item.hotel_id,
            "hotel": {
                "id": item.hotel.id,
                "name": item.hotel.name,
                "location": item.hotel.location,
                "price_per_night": float(item.hotel.price_per_night),
                "total_price": float(item.hotel.total_price),
                "rating": float(item.hotel.rating) if item.hotel.rating else None,
                "url": item.hotel.url,
                "site": item.hotel.site,
            }
        })
    
    return item_data


@router.patch("/{watchlist_id}")
async def update_watchlist_item(
    watchlist_id: int,
    request: UpdateWatchlistRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """Update watchlist item."""
    try:
        updates = {k: v for k, v in request.dict().items() if v is not None}
        watchlist = TravelWatchlistService.update_watchlist(
            db, watchlist_id, current_user.id, **updates
        )
        return {
            "id": watchlist.id,
            "target_price": float(watchlist.target_price) if watchlist.target_price else None,
            "alert_on_any_drop": watchlist.alert_on_any_drop,
            "alert_on_target": watchlist.alert_on_target,
            "notes": watchlist.notes,
            "updated_at": watchlist.updated_at,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{watchlist_id}")
async def remove_from_watchlist(
    watchlist_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """Remove item from watchlist."""
    success = TravelWatchlistService.remove_from_watchlist(db, watchlist_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    return {"message": "Item removed from watchlist"}