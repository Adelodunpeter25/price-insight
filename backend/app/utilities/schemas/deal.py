"""Utility deal schemas."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel

from app.utils.pagination import PaginatedResponse


class UtilityDealCreate(BaseModel):
    """Schema for creating utility deal."""

    service_id: int
    deal_type: str
    discount_percent: Optional[Decimal] = None
    original_price: Optional[Decimal] = None
    deal_price: Decimal
    deal_start_date: Optional[datetime] = None
    deal_end_date: Optional[datetime] = None
    deal_source: str = "manual"
    deal_description: Optional[str] = None


class UtilityDealResponse(BaseModel):
    """Schema for utility deal response."""

    id: int
    service_id: int
    deal_type: str
    discount_percent: Optional[Decimal]
    original_price: Optional[Decimal]
    deal_price: Decimal
    deal_start_date: Optional[datetime]
    deal_end_date: Optional[datetime]
    deal_source: str
    deal_description: Optional[str]
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class UtilityDealListResponse(PaginatedResponse):
    """Schema for paginated utility deal list."""

    items: List[UtilityDealResponse]
