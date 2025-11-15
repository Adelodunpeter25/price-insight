"""Property price analytics schemas."""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class PricePoint(BaseModel):
    """Price point for charting."""

    date: str
    price: float
    price_per_sqm: Optional[float]


class PeriodStats(BaseModel):
    """Price statistics for a period."""

    property_id: int
    period_days: int
    current_price: float
    lowest_price: float
    highest_price: float
    average_price: float
    price_drop: float
    price_drop_percentage: float
    savings_from_average: float
    savings_percentage: float
    data_points: int


class MultiPeriodStats(BaseModel):
    """Statistics for multiple periods."""

    last_7_days: Optional[PeriodStats]
    last_30_days: Optional[PeriodStats]
    last_60_days: Optional[PeriodStats]
    last_90_days: Optional[PeriodStats]
    trend_7_days: str
    trend_30_days: str


class PropertyAnalyticsResponse(BaseModel):
    """Complete analytics response."""

    property_id: int
    property_name: str
    current_price: float
    statistics: MultiPeriodStats
    price_history: List[PricePoint]
    volatility: Dict
    is_good_deal: bool
    trend: str
