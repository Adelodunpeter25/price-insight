"""Property watchlist schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class PropertyWatchlistCreate(BaseModel):
    """Schema for creating watchlist item."""

    property_name: str = Field(..., description="Property name or URL")
    target_price: Optional[Decimal] = Field(None, description="Target price alert")
    alert_on_any_drop: bool = Field(True, description="Alert on any price drop")
    alert_on_target: bool = Field(True, description="Alert when target price reached")
    notes: Optional[str] = Field(None, max_length=500, description="User notes")


class PropertyWatchlistUpdate(BaseModel):
    """Schema for updating watchlist item."""

    target_price: Optional[Decimal] = None
    alert_on_any_drop: Optional[bool] = None
    alert_on_target: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=500)


class PropertyWatchlistResponse(BaseModel):
    """Schema for watchlist response."""

    id: int
    user_id: int
    property_id: int
    target_price: Optional[Decimal]
    alert_on_any_drop: bool
    alert_on_target: bool
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
