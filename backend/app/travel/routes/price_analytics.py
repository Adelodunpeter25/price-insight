"""Travel price analytics API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_database_session
from app.travel.services.price_analytics import TravelPriceAnalytics

router = APIRouter(prefix="/api/travel/analytics", tags=["Travel Analytics"])


@router.get("/flights/{flight_id}")
async def get_flight_analytics(
    flight_id: int,
    days: int = 30,
    db: Session = Depends(get_database_session)
):
    """Get complete analytics for a flight."""
    stats = TravelPriceAnalytics.get_flight_price_stats(db, flight_id, days)
    if not stats:
        raise HTTPException(status_code=404, detail="Flight not found or no price data")
    
    trend = TravelPriceAnalytics.get_price_trend(db, flight_id, "flight", 7)
    volatility = TravelPriceAnalytics.get_price_volatility(db, flight_id, "flight", days)
    is_deal = TravelPriceAnalytics.is_good_deal(db, flight_id, "flight")
    
    return {
        "stats": stats,
        "trend": trend,
        "volatility": volatility,
        "is_good_deal": is_deal
    }


@router.get("/hotels/{hotel_id}")
async def get_hotel_analytics(
    hotel_id: int,
    days: int = 30,
    db: Session = Depends(get_database_session)
):
    """Get complete analytics for a hotel."""
    stats = TravelPriceAnalytics.get_hotel_price_stats(db, hotel_id, days)
    if not stats:
        raise HTTPException(status_code=404, detail="Hotel not found or no price data")
    
    trend = TravelPriceAnalytics.get_price_trend(db, hotel_id, "hotel", 7)
    volatility = TravelPriceAnalytics.get_price_volatility(db, hotel_id, "hotel", days)
    is_deal = TravelPriceAnalytics.is_good_deal(db, hotel_id, "hotel")
    
    return {
        "stats": stats,
        "trend": trend,
        "volatility": volatility,
        "is_good_deal": is_deal
    }


@router.get("/flights/{flight_id}/stats")
async def get_flight_stats(
    flight_id: int,
    days: int = 30,
    db: Session = Depends(get_database_session)
):
    """Get price statistics for a flight."""
    stats = TravelPriceAnalytics.get_flight_price_stats(db, flight_id, days)
    if not stats:
        raise HTTPException(status_code=404, detail="Flight not found or no price data")
    return stats


@router.get("/hotels/{hotel_id}/stats")
async def get_hotel_stats(
    hotel_id: int,
    days: int = 30,
    db: Session = Depends(get_database_session)
):
    """Get price statistics for a hotel."""
    stats = TravelPriceAnalytics.get_hotel_price_stats(db, hotel_id, days)
    if not stats:
        raise HTTPException(status_code=404, detail="Hotel not found or no price data")
    return stats


@router.get("/flights/{flight_id}/trend")
async def get_flight_trend(
    flight_id: int,
    days: int = 7,
    db: Session = Depends(get_database_session)
):
    """Get price trend for a flight."""
    trend = TravelPriceAnalytics.get_price_trend(db, flight_id, "flight", days)
    return {"flight_id": flight_id, "trend": trend, "period_days": days}


@router.get("/hotels/{hotel_id}/trend")
async def get_hotel_trend(
    hotel_id: int,
    days: int = 7,
    db: Session = Depends(get_database_session)
):
    """Get price trend for a hotel."""
    trend = TravelPriceAnalytics.get_price_trend(db, hotel_id, "hotel", days)
    return {"hotel_id": hotel_id, "trend": trend, "period_days": days}


@router.get("/flights/{flight_id}/history")
async def get_flight_history(
    flight_id: int,
    days: int = 30,
    db: Session = Depends(get_database_session)
):
    """Get price history chart data for a flight."""
    history = TravelPriceAnalytics.get_price_history_chart(db, flight_id, "flight", days)
    return {"flight_id": flight_id, "history": history, "period_days": days}


@router.get("/hotels/{hotel_id}/history")
async def get_hotel_history(
    hotel_id: int,
    days: int = 30,
    db: Session = Depends(get_database_session)
):
    """Get price history chart data for a hotel."""
    history = TravelPriceAnalytics.get_price_history_chart(db, hotel_id, "hotel", days)
    return {"hotel_id": hotel_id, "history": history, "period_days": days}


@router.get("/flights/{flight_id}/multi-period")
async def get_flight_multi_period_stats(
    flight_id: int,
    db: Session = Depends(get_database_session)
):
    """Get multi-period statistics for a flight."""
    stats = TravelPriceAnalytics.get_multi_period_stats(db, flight_id, "flight")
    return {"flight_id": flight_id, **stats}


@router.get("/hotels/{hotel_id}/multi-period")
async def get_hotel_multi_period_stats(
    hotel_id: int,
    db: Session = Depends(get_database_session)
):
    """Get multi-period statistics for a hotel."""
    stats = TravelPriceAnalytics.get_multi_period_stats(db, hotel_id, "hotel")
    return {"hotel_id": hotel_id, **stats}


@router.get("/destinations/{destination}/trends")
async def get_destination_trends(
    destination: str,
    days: int = 30,
    db: Session = Depends(get_database_session)
):
    """Get price trends for a destination."""
    trends = TravelPriceAnalytics.get_destination_price_trends(db, destination, days)
    return trends