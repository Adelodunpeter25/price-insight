"""Pydantic schemas for price analytics."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class PricePoint(BaseModel):
    """Single price point for charting."""
    
    date: datetime
    price: float
    availability: Optional[str] = None


class PriceStats(BaseModel):
    """Price statistics for a time period."""
    
    current_price: float
    lowest_price: float
    highest_price: float
    average_price: float
    price_drop_percentage: float
    savings_from_average: float
    savings_percentage: float
    data_points: int
    period_days: int
    first_tracked: str
    last_updated: str


class MultiPeriodStats(BaseModel):
    """Price statistics across multiple time periods."""
    
    last_7_days: Optional[PriceStats] = None
    last_30_days: Optional[PriceStats] = None
    last_60_days: Optional[PriceStats] = None
    last_90_days: Optional[PriceStats] = None
    trend_7_days: str
    trend_30_days: str


class PriceAnalyticsResponse(BaseModel):
    """Complete price analytics response."""
    
    product_id: int
    product_name: str
    current_price: float
    statistics: MultiPeriodStats
    price_history: List[PricePoint]
    volatility: Optional[float] = None
    is_good_deal: bool
    trend: str = Field(description="Overall price trend: rising, falling, stable")
