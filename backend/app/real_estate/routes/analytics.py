"""Property analytics dashboard API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.cache import cached
from app.core.constants import (
    CACHE_TTL_ANALYTICS_MOST_TRACKED,
    CACHE_TTL_ANALYTICS_PRICE_DROPS,
    CACHE_TTL_ANALYTICS_RETAILERS,
    CACHE_TTL_ANALYTICS_SAVINGS,
    CACHE_TTL_GLOBAL_DASHBOARD,
    CACHE_TTL_USER_DASHBOARD,
)
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.models.user import User
from app.real_estate.schemas.analytics import (
    GlobalDashboard,
    LocationStats,
    PriceDropStats,
    SavingsStats,
    TrackedProperty,
    UserDashboard,
)
from app.real_estate.services.analytics_dashboard import PropertyAnalyticsDashboard

router = APIRouter(
    prefix="/api/real-estate/analytics/dashboard", tags=["Real Estate Analytics Dashboard"]
)


@router.get("/user", response_model=UserDashboard)
@cached(ttl=CACHE_TTL_USER_DASHBOARD, key_prefix="property_dashboard:user")
async def get_user_dashboard(
    days: int = Query(30, ge=1, le=365, description="Days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user-specific analytics dashboard."""
    dashboard = PropertyAnalyticsDashboard.get_user_dashboard(db, current_user.id, days)
    return UserDashboard(**dashboard)


@router.get("/global", response_model=GlobalDashboard)
@cached(ttl=CACHE_TTL_GLOBAL_DASHBOARD, key_prefix="property_dashboard:global")
async def get_global_dashboard(
    days: int = Query(30, ge=1, le=365, description="Days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get global analytics dashboard."""
    dashboard = PropertyAnalyticsDashboard.get_global_dashboard(db, days)
    return GlobalDashboard(**dashboard)


@router.get("/savings", response_model=SavingsStats)
@cached(ttl=CACHE_TTL_ANALYTICS_SAVINGS, key_prefix="property_analytics:savings")
async def get_savings_stats(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get total savings statistics."""
    stats = PropertyAnalyticsDashboard.get_total_savings(db, current_user.id, days)
    return SavingsStats(**stats)


@router.get("/most-tracked")
@cached(ttl=CACHE_TTL_ANALYTICS_MOST_TRACKED, key_prefix="property_analytics:most_tracked")
async def get_most_tracked(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get most tracked properties."""
    properties = PropertyAnalyticsDashboard.get_most_tracked_properties(db, limit)
    return {"count": len(properties), "properties": [TrackedProperty(**p) for p in properties]}


@router.get("/best-value-areas")
@cached(ttl=CACHE_TTL_ANALYTICS_RETAILERS, key_prefix="property_analytics:best_areas")
async def get_best_value_areas(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get locations with best value."""
    areas = PropertyAnalyticsDashboard.get_best_value_areas(db, days, limit)
    return {
        "count": len(areas),
        "period_days": days,
        "areas": [LocationStats(**a) for a in areas],
    }


@router.get("/price-drops", response_model=PriceDropStats)
@cached(ttl=CACHE_TTL_ANALYTICS_PRICE_DROPS, key_prefix="property_analytics:price_drops")
async def get_price_drops(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get price drop statistics."""
    stats = PropertyAnalyticsDashboard.get_price_drop_statistics(db, days)
    return PriceDropStats(**stats)
