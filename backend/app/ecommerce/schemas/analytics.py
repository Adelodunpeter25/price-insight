"""Pydantic schemas for analytics dashboard."""

from typing import List, Optional

from pydantic import BaseModel


class SavingsStats(BaseModel):
    """Savings statistics."""
    
    total_deals: int
    total_savings: float
    average_discount: float
    period_days: int


class TrackedProduct(BaseModel):
    """Most tracked product."""
    
    product_id: int
    name: str
    site: str
    url: str
    watchlist_count: int
    current_price: Optional[float]


class RetailerStats(BaseModel):
    """Retailer performance statistics."""
    
    retailer: str
    deal_count: int
    total_savings: float
    average_discount: float


class BiggestDrop(BaseModel):
    """Biggest price drop."""
    
    product: str
    product_id: int
    amount: float
    percent: float
    old_price: float
    new_price: float


class PriceDropStats(BaseModel):
    """Price drop statistics."""
    
    total_products_tracked: int
    products_with_price_drops: int
    drop_rate_percent: float
    average_drop_amount: float
    average_drop_percent: float
    biggest_drop: Optional[BiggestDrop]
    period_days: int


class UserDashboard(BaseModel):
    """User-specific dashboard."""
    
    watchlist_count: int
    potential_savings: float
    items_at_target_price: int
    total_savings: SavingsStats
    most_tracked: List[TrackedProduct]
    best_retailers: List[RetailerStats]
    price_drops: PriceDropStats


class GlobalDashboard(BaseModel):
    """Global analytics dashboard."""
    
    total_products_tracked: int
    total_active_deals: int
    total_users_tracking: int
    total_savings: SavingsStats
    most_tracked_products: List[TrackedProduct]
    best_retailers: List[RetailerStats]
    price_drop_statistics: PriceDropStats
