"""Pydantic schemas for watchlist."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class WatchlistCreate(BaseModel):
    """Schema for creating watchlist item."""
    
    product_name: str = Field(..., min_length=1, max_length=500, description="Product name or URL")
    target_price: Optional[Decimal] = None
    alert_on_any_drop: bool = True
    alert_on_target: bool = True
    notes: Optional[str] = Field(None, max_length=500)


class WatchlistUpdate(BaseModel):
    """Schema for updating watchlist item."""
    
    target_price: Optional[Decimal] = None
    alert_on_any_drop: Optional[bool] = None
    alert_on_target: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=500)


class WatchlistResponse(BaseModel):
    """Schema for watchlist response."""
    
    id: int
    user_id: int
    product_id: int
    target_price: Optional[Decimal]
    alert_on_any_drop: bool
    alert_on_target: bool
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WatchlistWithProduct(WatchlistResponse):
    """Schema for watchlist with product details."""
    
    product_name: str
    product_url: str
    product_site: str
    current_price: Optional[Decimal]
    price_status: str = Field(description="above_target, at_target, below_target, no_target")
