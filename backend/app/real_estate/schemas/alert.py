"""Property alert schemas."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel

from app.utils.pagination import PaginatedResponse


class PropertyAlertRuleCreate(BaseModel):
    """Schema for creating property alert rule."""

    property_id: Optional[int] = None
    location: Optional[str] = None
    property_type: Optional[str] = None
    max_price: Optional[Decimal] = None
    min_bedrooms: Optional[int] = None
    rule_type: str  # price_drop, new_listing, location_alert
    threshold_value: Optional[Decimal] = None
    percentage_threshold: Optional[Decimal] = None
    notification_method: str = "console"


class PropertyAlertRuleResponse(BaseModel):
    """Schema for property alert rule response."""

    id: int
    property_id: Optional[int]
    location: Optional[str]
    property_type: Optional[str]
    max_price: Optional[Decimal]
    min_bedrooms: Optional[int]
    rule_type: str
    threshold_value: Optional[Decimal]
    percentage_threshold: Optional[Decimal]
    notification_method: str
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class PropertyAlertListResponse(PaginatedResponse):
    """Schema for paginated property alert list."""

    items: List[PropertyAlertRuleResponse]