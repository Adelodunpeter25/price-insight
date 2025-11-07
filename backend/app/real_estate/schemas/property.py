"""Property schemas for API requests and responses."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl

from app.utils.pagination import PaginatedResponse


class PropertyCreate(BaseModel):
    """Schema for creating property tracking."""

    name: str = Field(..., min_length=1, max_length=200)
    property_type: str = Field(..., description="house, apartment, land, commercial")
    location: str = Field(..., min_length=1, max_length=200)
    bedrooms: Optional[int] = Field(None, ge=0, le=20)
    bathrooms: Optional[int] = Field(None, ge=0, le=20)
    size_sqm: Optional[Decimal] = Field(None, ge=0)
    listing_type: str = Field("sale", description="sale or rent")
    url: HttpUrl = Field(..., description="Property listing URL")
    site: str = Field(..., description="Real estate site name")
    features: Optional[List[str]] = Field(None, description="Property features")


class PropertyUpdate(BaseModel):
    """Schema for updating property."""

    name: Optional[str] = None
    is_tracked: Optional[bool] = None


class PropertyPriceHistoryResponse(BaseModel):
    """Schema for property price history response."""

    id: int
    price: Decimal
    price_per_sqm: Optional[Decimal]
    currency: str
    listing_status: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PropertyResponse(BaseModel):
    """Schema for property response."""

    id: int
    name: str
    property_type: str
    location: str
    bedrooms: Optional[int]
    bathrooms: Optional[int]
    size_sqm: Optional[Decimal]
    price: Decimal
    price_per_sqm: Optional[Decimal]
    listing_type: str
    currency: str
    agent: Optional[str]
    url: str
    site: str
    features: Optional[str]
    is_tracked: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PropertyDetailResponse(PropertyResponse):
    """Schema for detailed property response with price history."""

    price_history: List[PropertyPriceHistoryResponse] = []


class PropertyListResponse(PaginatedResponse):
    """Schema for paginated property list response."""

    items: List[PropertyResponse]