"""Travel API schemas."""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl

from app.utils.pagination import PaginatedResponse


# Deal Schemas
class TravelDealCreate(BaseModel):
    """Schema for creating travel deal."""

    flight_id: Optional[int] = None
    hotel_id: Optional[int] = None
    discount_percent: Optional[float] = None
    original_price: Optional[float] = None
    deal_price: float
    deal_start_date: Optional[datetime] = None
    deal_end_date: Optional[datetime] = None
    deal_source: str = "manual"
    deal_description: Optional[str] = None


class TravelDealResponse(BaseModel):
    """Schema for travel deal response."""

    id: int
    flight_id: Optional[int] = None
    hotel_id: Optional[int] = None
    discount_percent: Optional[float] = None
    original_price: Optional[float] = None
    deal_price: float
    deal_start_date: Optional[datetime] = None
    deal_end_date: Optional[datetime] = None
    deal_source: str
    deal_description: Optional[str] = None
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class TravelDealListResponse(PaginatedResponse):
    """Schema for paginated travel deal list."""

    items: List[TravelDealResponse]


# Alert Schemas
class TravelAlertRuleCreate(BaseModel):
    """Schema for creating travel alert rule."""

    flight_id: Optional[int] = None
    hotel_id: Optional[int] = None
    rule_type: str  # price_drop, threshold, deal
    threshold_value: Optional[float] = None
    percentage_threshold: Optional[float] = None
    notification_method: str = "console"


class TravelAlertRuleResponse(BaseModel):
    """Schema for travel alert rule response."""

    id: int
    flight_id: Optional[int] = None
    hotel_id: Optional[int] = None
    rule_type: str
    threshold_value: Optional[float] = None
    percentage_threshold: Optional[float] = None
    notification_method: str
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class TravelAlertListResponse(PaginatedResponse):
    """Schema for paginated travel alert list."""

    items: List[TravelAlertRuleResponse]


class FlightCreate(BaseModel):
    """Schema for creating flight tracking."""

    origin: str = Field(..., min_length=3, max_length=10, description="Origin airport code")
    destination: str = Field(
        ..., min_length=3, max_length=10, description="Destination airport code"
    )
    departure_date: date = Field(..., description="Departure date")
    return_date: Optional[date] = Field(None, description="Return date for round trip")
    flight_class: str = Field("economy", description="Flight class")
    passengers: int = Field(1, ge=1, le=9, description="Number of passengers")
    url: HttpUrl = Field(..., description="Flight search URL")
    site: str = Field(..., description="Travel site name")


class FlightResponse(BaseModel):
    """Schema for flight response."""

    id: int
    origin: str
    destination: str
    departure_date: date
    return_date: Optional[date]
    airline: Optional[str]
    flight_class: str
    price: Decimal
    currency: str
    url: str
    site: str
    passengers: int
    is_tracked: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FlightListResponse(PaginatedResponse):
    """Schema for paginated flight list."""

    items: List[FlightResponse]


class HotelCreate(BaseModel):
    """Schema for creating hotel tracking."""

    name: str = Field(..., min_length=1, max_length=200, description="Hotel name")
    location: str = Field(..., min_length=1, max_length=200, description="Hotel location")
    check_in: date = Field(..., description="Check-in date")
    check_out: date = Field(..., description="Check-out date")
    room_type: str = Field(..., description="Room type")
    guests: int = Field(2, ge=1, le=10, description="Number of guests")
    url: HttpUrl = Field(..., description="Hotel booking URL")
    site: str = Field(..., description="Travel site name")


class HotelResponse(BaseModel):
    """Schema for hotel response."""

    id: int
    name: str
    location: str
    check_in: date
    check_out: date
    room_type: str
    price_per_night: Decimal
    total_price: Decimal
    currency: str
    url: str
    site: str
    guests: int
    rating: Optional[Decimal]
    is_tracked: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HotelListResponse(PaginatedResponse):
    """Schema for paginated hotel list."""

    items: List[HotelResponse]
