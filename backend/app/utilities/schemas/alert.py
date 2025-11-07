"""Utility alert schemas."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel

from app.utils.pagination import PaginatedResponse


class UtilityAlertRuleCreate(BaseModel):
    """Schema for creating utility alert rule."""

    service_id: Optional[int] = None
    service_type: Optional[str] = None
    provider: Optional[str] = None
    max_price: Optional[Decimal] = None
    rule_type: str  # price_increase, promotion, rate_change
    threshold_value: Optional[Decimal] = None
    percentage_threshold: Optional[Decimal] = None
    notification_method: str = "console"


class UtilityAlertRuleResponse(BaseModel):
    """Schema for utility alert rule response."""

    id: int
    service_id: Optional[int]
    service_type: Optional[str]
    provider: Optional[str]
    max_price: Optional[Decimal]
    rule_type: str
    threshold_value: Optional[Decimal]
    percentage_threshold: Optional[Decimal]
    notification_method: str
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class UtilityAlertListResponse(PaginatedResponse):
    """Schema for paginated utility alert list."""

    items: List[UtilityAlertRuleResponse]
