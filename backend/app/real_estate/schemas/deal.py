"""Property deal schemas."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel

from app.utils.pagination import PaginatedResponse


class PropertyDealCreate(BaseModel):
    """Schema for creating property deal."""

    property_id: int
    deal_type: str
    discount_percent: Optional[Decimal] = None
    original_price: Optional[Decimal] = None
    deal_price: Decimal
    deal_start_date: Optional[datetime] = None
    deal_end_date: Optional[datetime] = None
    deal_source: str = "manual"
    deal_description: Optional[str] = None


class PropertyDealResponse(BaseModel):
    """Schema for property deal response."""

    id: int
    property_id: int
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


class PropertyDealListResponse(PaginatedResponse):
    """Schema for paginated property deal list."""

    items: List[PropertyDealResponse]