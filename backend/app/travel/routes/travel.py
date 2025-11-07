"""Travel API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_database_session
from app.travel.models import Flight, Hotel
from app.travel.models.deal import TravelDeal
from app.travel.models.travel_alert import TravelAlertRule
from app.travel.schemas.travel import (
    FlightCreate,
    FlightListResponse,
    FlightResponse,
    HotelCreate,
    HotelListResponse,
    HotelResponse,
    TravelAlertListResponse,
    TravelAlertRuleCreate,
    TravelAlertRuleResponse,
    TravelDealCreate,
    TravelDealListResponse,
    TravelDealResponse,
)
from app.travel.services.deal_service import TravelDealService
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


# Deal Endpoints
@router.get("/deals", response_model=TravelDealListResponse)
async def list_deals(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_database_session),
):
    """List active travel deals."""
    deal_service = TravelDealService(db)
    deals = await deal_service.get_active_deals()
    
    # Simple pagination for deals
    start = (page - 1) * size
    end = start + size
    paginated_deals = deals[start:end]
    
    return TravelDealListResponse(
        items=[TravelDealResponse.model_validate(deal) for deal in paginated_deals],
        total=len(deals),
        page=page,
        size=size,
        pages=(len(deals) + size - 1) // size
    )


@router.get("/deals/{deal_id}", response_model=TravelDealResponse)
async def get_deal(
    deal_id: int, db: AsyncSession = Depends(get_database_session)
):
    """Get deal details."""
    deal_service = TravelDealService(db)
    deal = await deal_service.get_deal_by_id(deal_id)
    
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    return TravelDealResponse.model_validate(deal)


# Alert Endpoints
@router.post("/alerts/rules", response_model=TravelAlertRuleResponse, status_code=201)
async def create_alert_rule(
    alert_data: TravelAlertRuleCreate, db: AsyncSession = Depends(get_database_session)
):
    """Create travel alert rule."""
    alert_rule = TravelAlertRule(
        flight_id=alert_data.flight_id,
        hotel_id=alert_data.hotel_id,
        rule_type=alert_data.rule_type,
        threshold_value=alert_data.threshold_value,
        percentage_threshold=alert_data.percentage_threshold,
        notification_method=alert_data.notification_method,
    )
    
    db.add(alert_rule)
    await db.commit()
    await db.refresh(alert_rule)
    
    return TravelAlertRuleResponse.model_validate(alert_rule)


@router.get("/alerts", response_model=TravelAlertListResponse)
async def list_alerts(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_database_session),
):
    """List travel alerts."""
    query = select(TravelAlertRule).where(TravelAlertRule.is_active == True)
    query = query.order_by(TravelAlertRule.created_at.desc())
    
    pagination = PaginationParams(page=page, size=size)
    result = await paginate_query(db, query, pagination, TravelAlertRuleResponse)
    
    return TravelAlertListResponse(**result.model_dump())