"""Deal preference schemas."""

from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class DealPreferenceBase(BaseModel):
    """Base deal preference schema."""
    enable_deal_alerts: bool = True
    min_discount_percent: Decimal = Field(default=10.0, ge=0, le=100)
    max_price_threshold: Optional[Decimal] = Field(default=None, ge=0)
    deal_types: List[str] = Field(default=["percentage"])


class DealPreferenceCreate(DealPreferenceBase):
    """Schema for creating deal preferences."""
    product_id: int


class DealPreferenceUpdate(BaseModel):
    """Schema for updating deal preferences."""
    enable_deal_alerts: Optional[bool] = None
    min_discount_percent: Optional[Decimal] = Field(default=None, ge=0, le=100)
    max_price_threshold: Optional[Decimal] = Field(default=None, ge=0)
    deal_types: Optional[List[str]] = None


class DealPreferenceResponse(DealPreferenceBase):
    """Schema for deal preference responses."""
    id: int
    product_id: int
    user_id: int
    
    class Config:
        from_attributes = True