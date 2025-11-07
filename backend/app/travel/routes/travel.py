"""Travel API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_database_session
from app.travel.models import Flight, Hotel
from app.travel.schemas.travel import (
    FlightCreate,
    FlightListResponse,
    FlightResponse,
    HotelCreate,
    HotelListResponse,
    HotelResponse,
)
from app.travel.services.travel_service import TravelService
from app.utils.pagination import PaginationParams, paginate_query

router = APIRouter(prefix="/api/travel", tags=["Travel"])


@router.post("/flights", response_model=FlightResponse, status_code=201)
async def create_flight(
    flight_data: FlightCreate, db: AsyncSession = Depends(get_database_session)
):
    """Add flight to track."""
    travel_service = TravelService(db)
    
    try:
        flight = await travel_service.create_flight(
            origin=flight_data.origin,
            destination=flight_data.destination,
            departure_date=flight_data.departure_date,
            return_date=flight_data.return_date,
            flight_class=flight_data.flight_class,
            passengers=flight_data.passengers,
            url=flight_data.url,
            site=flight_data.site,
        )
        return FlightResponse.model_validate(flight)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create flight: {str(e)}")


@router.get("/flights", response_model=FlightListResponse)
async def list_flights(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    origin: Optional[str] = Query(None),
    destination: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_database_session),
):
    """List tracked flights."""
    query = select(Flight).where(Flight.is_active == True)
    
    if origin:
        query = query.where(Flight.origin.ilike(f"%{origin.upper()}%"))
    if destination:
        query = query.where(Flight.destination.ilike(f"%{destination.upper()}%"))
    
    query = query.order_by(Flight.departure_date.asc())
    
    pagination = PaginationParams(page=page, size=size)
    result = await paginate_query(db, query, pagination, FlightResponse)
    
    return FlightListResponse(**result.model_dump())


@router.post("/hotels", response_model=HotelResponse, status_code=201)
async def create_hotel(
    hotel_data: HotelCreate, db: AsyncSession = Depends(get_database_session)
):
    """Add hotel to track."""
    travel_service = TravelService(db)
    
    try:
        hotel = await travel_service.create_hotel(
            name=hotel_data.name,
            location=hotel_data.location,
            check_in=hotel_data.check_in,
            check_out=hotel_data.check_out,
            room_type=hotel_data.room_type,
            guests=hotel_data.guests,
            url=hotel_data.url,
            site=hotel_data.site,
        )
        return HotelResponse.model_validate(hotel)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create hotel: {str(e)}")


@router.get("/hotels", response_model=HotelListResponse)
async def list_hotels(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    location: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_database_session),
):
    """List tracked hotels."""
    query = select(Hotel).where(Hotel.is_active == True)
    
    if location:
        query = query.where(Hotel.location.ilike(f"%{location}%"))
    
    query = query.order_by(Hotel.check_in.asc())
    
    pagination = PaginationParams(page=page, size=size)
    result = await paginate_query(db, query, pagination, HotelResponse)
    
    return HotelListResponse(**result.model_dump())