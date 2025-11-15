"""Property price analytics API endpoints."""

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
from app.real_estate.models.property import Property
from app.real_estate.schemas.price_analytics import (
    MultiPeriodStats,
    PricePoint,
    PropertyAnalyticsResponse,
)
from app.real_estate.services.price_analytics import PropertyPriceAnalytics

router = APIRouter(prefix="/api/real-estate/analytics", tags=["Real Estate Price Analytics"])


@router.get("/properties/{property_id}", response_model=PropertyAnalyticsResponse)
@cached(ttl=CACHE_TTL_PRODUCT_ANALYTICS, key_prefix="property_analytics")
async def get_property_analytics(
    property_id: int,
    days: int = Query(30, ge=1, le=365, description="Days of history to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get comprehensive price analytics for a property."""
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")

    multi_stats = PropertyPriceAnalytics.get_multi_period_stats(db, property_id)
    history = PropertyPriceAnalytics.get_price_history_chart(db, property_id, days)
    volatility = PropertyPriceAnalytics.get_price_volatility(db, property_id, days)
    is_good_deal = PropertyPriceAnalytics.is_good_deal(db, property_id)
    trend = PropertyPriceAnalytics.get_price_trend(db, property_id, 7)

    current_price = history[-1]["price"] if history else float(property_obj.price)

    return PropertyAnalyticsResponse(
        property_id=property_id,
        property_name=property_obj.name,
        current_price=current_price,
        statistics=MultiPeriodStats(**multi_stats),
        price_history=[PricePoint(**p) for p in history],
        volatility=volatility,
        is_good_deal=is_good_deal,
        trend=trend,
    )


@router.get("/properties/{property_id}/stats")
@cached(ttl=CACHE_TTL_PRICE_STATS, key_prefix="property_price_stats")
async def get_price_stats(
    property_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get price statistics for a specific time period."""
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")

    stats = PropertyPriceAnalytics.get_price_stats(db, property_id, days)
    if not stats:
        raise HTTPException(status_code=404, detail="No price history found")

    return stats


@router.get("/properties/{property_id}/trend")
@cached(ttl=CACHE_TTL_PRICE_TREND, key_prefix="property_price_trend")
async def get_price_trend(
    property_id: int,
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get price trend for a property."""
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")

    trend = PropertyPriceAnalytics.get_price_trend(db, property_id, days)

    return {"property_id": property_id, "trend": trend, "period_days": days}


@router.get("/properties/{property_id}/history", response_model=List[PricePoint])
@cached(ttl=CACHE_TTL_PRICE_HISTORY, key_prefix="property_price_history")
async def get_price_history(
    property_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get price history for charting."""
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")

    history = PropertyPriceAnalytics.get_price_history_chart(db, property_id, days)

    return [PricePoint(**p) for p in history]


@router.get("/properties/{property_id}/deal-check")
async def check_if_good_deal(
    property_id: int,
    threshold: float = Query(10.0, ge=0, le=100, description="Discount threshold percentage"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check if current price is a good deal."""
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")

    is_deal = PropertyPriceAnalytics.is_good_deal(db, property_id, threshold)
    stats = PropertyPriceAnalytics.get_price_stats(db, property_id, 30)

    if not stats:
        raise HTTPException(status_code=404, detail="No price history found")

    return {
        "property_id": property_id,
        "is_good_deal": is_deal,
        "current_price": stats["current_price"],
        "average_price": stats["average_price"],
        "savings_percentage": stats["savings_percentage"],
        "threshold_percentage": threshold,
    }


@router.get("/locations/{location}/trends")
@cached(ttl=CACHE_TTL_PRICE_STATS, key_prefix="location_trends")
async def get_location_trends(
    location: str,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get price trends for a location."""
    trends = PropertyPriceAnalytics.get_location_price_trends(db, location, days)
    return trends
