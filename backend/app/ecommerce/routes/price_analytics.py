"""Price analytics API endpoints."""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.cache import cached
from app.core.constants import (
    CACHE_TTL_PRICE_HISTORY,
    CACHE_TTL_PRICE_STATS,
    CACHE_TTL_PRICE_TREND,
    CACHE_TTL_PRODUCT_ANALYTICS,
)
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.models.user import User
from app.ecommerce.models.product import Product
from app.ecommerce.schemas.price_analytics import (
    MultiPeriodStats,
    PriceAnalyticsResponse,
    PricePoint,
)
from app.ecommerce.services.price_analytics import PriceAnalytics

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["Price Analytics"])


@router.get("/products/{product_id}", response_model=PriceAnalyticsResponse)
@cached(ttl=CACHE_TTL_PRODUCT_ANALYTICS, key_prefix="analytics:product")
async def get_product_analytics(
    product_id: int,
    days: int = Query(30, ge=1, le=365, description="Days of history to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive price analytics for a product."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get multi-period statistics
    multi_stats = PriceAnalytics.get_multi_period_stats(db, product_id)
    
    # Get price history for charting
    history = PriceAnalytics.get_price_history_chart(db, product_id, days)
    
    # Get volatility
    volatility = PriceAnalytics.get_price_volatility(db, product_id, days)
    
    # Check if it's a good deal
    is_good_deal = PriceAnalytics.is_good_deal(db, product_id)
    
    # Get current trend
    trend = PriceAnalytics.get_price_trend(db, product_id, 7)
    
    # Get current price
    current_price = history[-1]["price"] if history else 0.0
    
    return PriceAnalyticsResponse(
        product_id=product_id,
        product_name=product.name,
        current_price=current_price,
        statistics=MultiPeriodStats(**multi_stats),
        price_history=[PricePoint(**p) for p in history],
        volatility=volatility,
        is_good_deal=is_good_deal,
        trend=trend
    )


@router.get("/products/{product_id}/stats")
@cached(ttl=CACHE_TTL_PRICE_STATS, key_prefix="price:stats")
async def get_price_stats(
    product_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get price statistics for a specific time period."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    stats = PriceAnalytics.get_price_stats(db, product_id, days)
    if not stats:
        raise HTTPException(status_code=404, detail="No price history found")
    
    return stats


@router.get("/products/{product_id}/trend")
@cached(ttl=CACHE_TTL_PRICE_TREND, key_prefix="price:trend")
async def get_price_trend(
    product_id: int,
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get price trend for a product."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    trend = PriceAnalytics.get_price_trend(db, product_id, days)
    
    return {
        "product_id": product_id,
        "trend": trend,
        "period_days": days
    }


@router.get("/products/{product_id}/history", response_model=List[PricePoint])
@cached(ttl=CACHE_TTL_PRICE_HISTORY, key_prefix="price:history")
async def get_price_history(
    product_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get price history for charting."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    history = PriceAnalytics.get_price_history_chart(db, product_id, days)
    
    return [PricePoint(**p) for p in history]


@router.get("/products/{product_id}/deal-check")
def check_if_good_deal(
    product_id: int,
    threshold: float = Query(10.0, ge=0, le=100, description="Discount threshold percentage"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if current price is a good deal."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    is_deal = PriceAnalytics.is_good_deal(db, product_id, threshold)
    stats = PriceAnalytics.get_price_stats(db, product_id, 30)
    
    if not stats:
        raise HTTPException(status_code=404, detail="No price history found")
    
    return {
        "product_id": product_id,
        "is_good_deal": is_deal,
        "current_price": stats["current_price"],
        "average_price": stats["average_price"],
        "savings_percentage": stats["savings_percentage"],
        "threshold_percentage": threshold
    }
