"""Travel schemas for API requests and responses."""

from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class FlightBase(BaseModel):
    """Base flight schema."""
    origin: str = Field(..., max_length=10, description="Origin airport code")
    destination: str = Field(..., max_length=10, description="Destination airport code")
    departure_date: date = Field(..., description="Departure date")
    return_date: Optional[date] = Field(None, description="Return date for round trip")
    airline: Optional[str] = Field(None, max_length=100, description="Airline name")
    flight_class: str = Field("economy", max_length=20, description="Flight class")
    passengers: int = Field(1, ge=1, le=9, description="Number of passengers")


class FlightCreate(FlightBase):
    """Schema for creating a flight."""
    url: str = Field(..., description="Flight booking URL")
    site: str = Field(..., max_length=100, description="Booking site")


class FlightResponse(FlightBase):
    """Schema for flight response."""
    id: int
    price: Decimal
    currency: str
    url: str
    site: str
    is_tracked: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class HotelBase(BaseModel):
    """Base hotel schema."""
    name: str = Field(..., max_length=200, description="Hotel name")
    location: str = Field(..., max_length=200, description="Hotel location")
    check_in: date = Field(..., description="Check-in date")
    check_out: date = Field(..., description="Check-out date")
    room_type: str = Field("standard", max_length=100, description="Room type")
    guests: int = Field(2, ge=1, le=10, description="Number of guests")


class HotelCreate(HotelBase):
    """Schema for creating a hotel."""
    url: str = Field(..., description="Hotel booking URL")
    site: str = Field(..., max_length=100, description="Booking site")


class HotelResponse(HotelBase):
    """Schema for hotel response."""
    id: int
    price_per_night: Decimal
    total_price: Decimal
    currency: str
    url: str
    site: str
    rating: Optional[Decimal]
    is_tracked: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class TravelWatchlistBase(BaseModel):
    """Base travel watchlist schema."""
    target_price: Optional[Decimal] = Field(None, description="Target price for alerts")
    alert_on_any_drop: bool = Field(True, description="Alert on any price drop")
    alert_on_target: bool = Field(True, description="Alert when target price reached")
    notes: Optional[str] = Field(None, max_length=500, description="User notes")


class TravelWatchlistCreate(TravelWatchlistBase):
    """Schema for creating travel watchlist item."""
    flight_id: Optional[int] = Field(None, description="Flight ID")
    hotel_id: Optional[int] = Field(None, description="Hotel ID")


class TravelWatchlistResponse(TravelWatchlistBase):
    """Schema for travel watchlist response."""
    id: int
    user_id: int
    flight_id: Optional[int]
    hotel_id: Optional[int]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class TravelDealResponse(BaseModel):
    """Schema for travel deal response."""
    id: int
    flight_id: Optional[int]
    hotel_id: Optional[int]
    original_price: Decimal
    deal_price: Decimal
    discount_percent: Decimal
    deal_type: str
    description: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class TravelPriceHistoryResponse(BaseModel):
    """Schema for travel price history response."""
    id: int
    flight_id: Optional[int]
    hotel_id: Optional[int]
    price: Decimal
    currency: str
    source: str
    created_at: str

    class Config:
        from_attributes = True