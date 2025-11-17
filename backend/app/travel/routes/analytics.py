"""Travel analytics dashboard API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_database_session
from app.core.models.user import User
from app.travel.services.analytics_dashboard import TravelAnalyticsDashboard

router = APIRouter(prefix="/api/travel/analytics", tags=["Travel Analytics Dashboard"])


@router.get("/dashboard/user")
async def get_user_dashboard(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """Get user-specific travel dashboard metrics."""
    dashboard = TravelAnalyticsDashboard.get_user_dashboard(db, current_user.id, days)
    return dashboard


@router.get("/dashboard/global")
async def get_global_dashboard(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_database_session)
):
    """Get platform-wide travel dashboard metrics."""
    dashboard = TravelAnalyticsDashboard.get_global_dashboard(db, days)
    return dashboard


@router.get("/dashboard/savings")
async def get_savings_dashboard(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """Get total savings statistics for user."""
    savings = TravelAnalyticsDashboard.get_total_savings(db, current_user.id, days)
    return savings


@router.get("/dashboard/destinations")
async def get_most_searched_destinations(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of destinations"),
    db: Session = Depends(get_database_session)
):
    """Get most searched travel destinations."""
    destinations = TravelAnalyticsDashboard.get_most_searched_destinations(db, limit)
    return {
        "destinations": destinations,
        "total": len(destinations)
    }


@router.get("/dashboard/deals")
async def get_best_travel_deals(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of deals"),
    db: Session = Depends(get_database_session)
):
    """Get best travel deals by discount percentage."""
    deals = TravelAnalyticsDashboard.get_best_travel_deals(db, days, limit)
    return {
        "deals": deals,
        "total": len(deals),
        "period_days": days
    }


@router.get("/dashboard/price-drops")
async def get_price_drop_statistics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_database_session)
):
    """Get travel price drop statistics."""
    stats = TravelAnalyticsDashboard.get_price_drop_statistics(db, days)
    return stats