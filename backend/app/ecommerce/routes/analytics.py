"""Analytics dashboard API endpoints."""

import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.cache import cached, invalidate_cache
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
from app.ecommerce.schemas.analytics import (
    GlobalDashboard,
    PriceDropStats,
    RetailerStats,
    SavingsStats,
    TrackedProduct,
    UserDashboard,
)
from app.ecommerce.services.analytics_dashboard import AnalyticsDashboard

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics/dashboard", tags=["Analytics Dashboard"])


@router.get("/user", response_model=UserDashboard)
@cached(ttl=CACHE_TTL_USER_DASHBOARD, key_prefix="dashboard:user")
async def get_user_dashboard(
    days: int = Query(30, ge=1, le=365, description="Days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user-specific analytics dashboard."""
    dashboard = AnalyticsDashboard.get_user_dashboard(db, current_user.id, days)
    return UserDashboard(**dashboard)


@router.get("/global", response_model=GlobalDashboard)
@cached(ttl=CACHE_TTL_GLOBAL_DASHBOARD, key_prefix="dashboard:global")
async def get_global_dashboard(
    days: int = Query(30, ge=1, le=365, description="Days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get global analytics dashboard."""
    dashboard = AnalyticsDashboard.get_global_dashboard(db, days)
    return GlobalDashboard(**dashboard)


@router.get("/savings", response_model=SavingsStats)
@cached(ttl=CACHE_TTL_ANALYTICS_SAVINGS, key_prefix="analytics:savings")
async def get_savings_stats(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get total savings statistics."""
    stats = AnalyticsDashboard.get_total_savings(db, current_user.id, days)
    return SavingsStats(**stats)


@router.get("/most-tracked")
@cached(ttl=CACHE_TTL_ANALYTICS_MOST_TRACKED, key_prefix="analytics:most_tracked")
async def get_most_tracked(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get most tracked products."""
    products = AnalyticsDashboard.get_most_tracked_products(db, limit)
    return {
        "count": len(products),
        "products": [TrackedProduct(**p) for p in products]
    }


@router.get("/retailers")
@cached(ttl=CACHE_TTL_ANALYTICS_RETAILERS, key_prefix="analytics:retailers")
async def get_best_retailers(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get best performing retailers."""
    retailers = AnalyticsDashboard.get_best_retailers(db, days, limit)
    return {
        "count": len(retailers),
        "period_days": days,
        "retailers": [RetailerStats(**r) for r in retailers]
    }


@router.get("/price-drops", response_model=PriceDropStats)
@cached(ttl=CACHE_TTL_ANALYTICS_PRICE_DROPS, key_prefix="analytics:price_drops")
async def get_price_drops(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get price drop statistics."""
    stats = AnalyticsDashboard.get_price_drop_statistics(db, days)
    return PriceDropStats(**stats)
