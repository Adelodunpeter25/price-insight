"""Travel alert schemas."""

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class TravelAlertRuleCreate(BaseModel):
    """Schema for creating travel alert rule."""
    flight_id: Optional[int] = Field(None, description="Flight ID")
    hotel_id: Optional[int] = Field(None, description="Hotel ID")
    rule_type: str = Field(..., description="Alert rule type")
    threshold_value: Optional[Decimal] = Field(None, description="Threshold value")
    percentage_threshold: Optional[Decimal] = Field(None, description="Percentage threshold")
    notification_method: str = Field("email", description="Notification method")


class TravelAlertRuleResponse(BaseModel):
    """Schema for travel alert rule response."""
    id: int
    flight_id: Optional[int]
    hotel_id: Optional[int]
    rule_type: str
    threshold_value: Optional[Decimal]
    percentage_threshold: Optional[Decimal]
    notification_method: str
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True