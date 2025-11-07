"""Travel API schemas."""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl

from app.utils.pagination import PaginatedResponse


class FlightCreate(BaseModel):
    """Schema for creating flight tracking."""

    origin: str = Field(..., min_length=3, max_length=10, description="Origin airport code")
    destination: str = Field(..., min_length=3, max_length=10, description="Destination airport code")
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