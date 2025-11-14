"""Watchlist API endpoints."""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.models.user import User
from app.ecommerce.models.price_history import PriceHistory
from app.ecommerce.models.product import Product
from app.ecommerce.schemas.watchlist import (
    WatchlistCreate,
    WatchlistResponse,
    WatchlistUpdate,
    WatchlistWithProduct,
)
from app.ecommerce.services.watchlist_service import WatchlistService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])


@router.post("", response_model=WatchlistResponse, status_code=201)
async def add_to_watchlist(
    data: WatchlistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add product to watchlist by name or URL."""
    watchlist = await WatchlistService.add_to_watchlist(
        db=db,
        user_id=current_user.id,
        product_name_or_url=data.product_name,
        target_price=data.target_price,
        alert_on_any_drop=data.alert_on_any_drop,
        alert_on_target=data.alert_on_target,
        notes=data.notes
    )
    
    if not watchlist:
        raise HTTPException(
            status_code=400, 
            detail="Failed to add to watchlist. Product not found or could not be scraped."
        )
    
    return watchlist


@router.get("", response_model=List[WatchlistWithProduct])
def get_watchlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's watchlist with product details."""
    watchlists = WatchlistService.get_user_watchlist(db, current_user.id)
    
    result = []
    for watchlist in watchlists:
        product = db.query(Product).filter(Product.id == watchlist.product_id).first()
        if not product:
            continue
        
        # Get current price
        latest_price = db.query(PriceHistory).filter(
            PriceHistory.product_id == product.id
        ).order_by(PriceHistory.created_at.desc()).first()
        
        current_price = latest_price.price if latest_price else None
        
        # Determine price status
        price_status = "no_target"
        if watchlist.target_price and current_price:
            if current_price <= watchlist.target_price:
                price_status = "at_or_below_target"
            else:
                price_status = "above_target"
        
        result.append(
            WatchlistWithProduct(
                id=watchlist.id,
                user_id=watchlist.user_id,
                product_id=watchlist.product_id,
                target_price=watchlist.target_price,
                alert_on_any_drop=watchlist.alert_on_any_drop,
                alert_on_target=watchlist.alert_on_target,
                notes=watchlist.notes,
                created_at=watchlist.created_at,
                updated_at=watchlist.updated_at,
                product_name=product.name,
                product_url=product.url,
                product_site=product.site,
                current_price=current_price,
                price_status=price_status
            )
        )
    
    return result


@router.get("/{watchlist_id}", response_model=WatchlistResponse)
def get_watchlist_item(
    watchlist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific watchlist item."""
    from app.ecommerce.models.watchlist import Watchlist
    
    watchlist = db.query(Watchlist).filter(
        Watchlist.id == watchlist_id,
        Watchlist.user_id == current_user.id
    ).first()
    
    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    
    return watchlist


@router.patch("/{watchlist_id}", response_model=WatchlistResponse)
def update_watchlist_item(
    watchlist_id: int,
    data: WatchlistUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update watchlist item."""
    watchlist = WatchlistService.update_watchlist(
        db=db,
        user_id=current_user.id,
        watchlist_id=watchlist_id,
        target_price=data.target_price,
        alert_on_any_drop=data.alert_on_any_drop,
        alert_on_target=data.alert_on_target,
        notes=data.notes
    )
    
    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    
    return watchlist


@router.delete("/{watchlist_id}", status_code=204)
def remove_from_watchlist(
    watchlist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove product from watchlist."""
    success = WatchlistService.remove_from_watchlist(db, current_user.id, watchlist_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    
    return None
