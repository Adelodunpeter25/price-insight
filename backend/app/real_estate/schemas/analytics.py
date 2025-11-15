"""Property analytics dashboard schemas."""

from typing import List, Optional

from pydantic import BaseModel


class TrackedProperty(BaseModel):
    """Tracked property summary."""

    property_id: int
    name: str
    location: str
    price: float
    property_type: str
    watchlist_count: int


class LocationStats(BaseModel):
    """Location statistics."""

    location: str
    deal_count: int
    total_savings: float
    average_discount: float


class PriceDropStats(BaseModel):
    """Price drop statistics."""

    total_properties: int
    properties_with_drops: int
    drop_rate_percentage: float
    average_drop_amount: float
    average_drop_percentage: float
    biggest_drop: Optional[dict]
    period_days: int


class SavingsStats(BaseModel):
    """Savings statistics."""

    total_deals: int
    total_savings: float
    average_discount: float
    period_days: int


class UserDashboard(BaseModel):
    """User dashboard response."""

    watchlist_count: int
    deals_on_watchlist: int
    potential_savings: float
    period_days: int


class GlobalDashboard(BaseModel):
    """Global dashboard response."""

    total_properties_tracked: int
    total_active_deals: int
    total_savings: float
    total_users_tracking: int
    period_days: int
