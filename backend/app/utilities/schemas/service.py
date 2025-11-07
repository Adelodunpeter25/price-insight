"""Utility service schemas for API requests and responses."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl

from app.utils.pagination import PaginatedResponse


class UtilityServiceCreate(BaseModel):
    """Schema for creating utility service tracking."""

    name: str = Field(..., min_length=1, max_length=200)
    service_type: str = Field(..., description="electricity, water, internet, streaming, software")
    provider: str = Field(..., min_length=1, max_length=100)
    billing_type: str = Field("subscription", description="prepaid, postpaid, subscription")
    billing_cycle: Optional[str] = Field(None, description="monthly, quarterly, yearly")
    plan_details: Optional[str] = Field(None, description="Plan features and details")
    url: HttpUrl = Field(..., description="Service pricing URL")
    site: str = Field(..., description="Provider website")


class UtilityServiceUpdate(BaseModel):
    """Schema for updating utility service."""

    name: Optional[str] = None
    is_tracked: Optional[bool] = None


class UtilityPriceHistoryResponse(BaseModel):
    """Schema for utility price history response."""

    id: int
    price: Decimal
    currency: str
    tariff_details: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class UtilityServiceResponse(BaseModel):
    """Schema for utility service response."""

    id: int
    name: str
    service_type: str
    provider: str
    billing_type: str
    billing_cycle: Optional[str]
    base_price: Decimal
    currency: str
    plan_details: Optional[str]
    url: str
    site: str
    is_tracked: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UtilityServiceDetailResponse(UtilityServiceResponse):
    """Schema for detailed utility service response with price history."""

    price_history: List[UtilityPriceHistoryResponse] = []


class UtilityServiceListResponse(PaginatedResponse):
    """Schema for paginated utility service list response."""

    items: List[UtilityServiceResponse]
