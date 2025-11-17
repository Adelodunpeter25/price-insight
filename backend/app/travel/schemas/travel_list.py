"""Travel list response schemas."""

from typing import List

from pydantic import BaseModel

from .travel import FlightResponse, HotelResponse, TravelDealResponse, TravelWatchlistResponse


class FlightListResponse(BaseModel):
    """Schema for flight list response."""
    items: List[FlightResponse]
    total: int
    page: int = 1
    size: int = 20
    pages: int = 1


class HotelListResponse(BaseModel):
    """Schema for hotel list response."""
    items: List[HotelResponse]
    total: int
    page: int = 1
    size: int = 20
    pages: int = 1


class TravelDealListResponse(BaseModel):
    """Schema for travel deal list response."""
    items: List[TravelDealResponse]
    total: int
    page: int = 1
    size: int = 20
    pages: int = 1


class TravelAlertListResponse(BaseModel):
    """Schema for travel alert list response."""
    items: List[dict]
    total: int
    page: int = 1
    size: int = 20
    pages: int = 1