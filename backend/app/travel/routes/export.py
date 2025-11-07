"""Travel export endpoints."""

from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_database_session
from app.core.models.user import User
from app.travel.models import Flight, Hotel
from app.utils.export import export_service

router = APIRouter(prefix="/api/travel/export", tags=["Travel Export"])


@router.get("/flights/csv")
async def export_flights_csv(
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    """Export flights to CSV."""
    query = select(Flight).where(Flight.is_active)
    result = await db.execute(query)
    flights = result.scalars().all()

    data = export_service.prepare_travel_data(flights, "flights")
    csv_output = export_service.generate_csv(data, "flights.csv")

    return Response(
        content=csv_output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=flights.csv"},
    )


@router.get("/flights/pdf")
async def export_flights_pdf(
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    """Export flights to PDF."""
    query = select(Flight).where(Flight.is_active)
    result = await db.execute(query)
    flights = result.scalars().all()

    data = export_service.prepare_travel_data(flights, "flights")
    pdf_output = export_service.generate_pdf(data, "Flights Report", "flights.pdf")

    return Response(
        content=pdf_output.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=flights.pdf"},
    )


@router.get("/hotels/csv")
async def export_hotels_csv(
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    """Export hotels to CSV."""
    query = select(Hotel).where(Hotel.is_active)
    result = await db.execute(query)
    hotels = result.scalars().all()

    data = export_service.prepare_travel_data(hotels, "hotels")
    csv_output = export_service.generate_csv(data, "hotels.csv")

    return Response(
        content=csv_output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=hotels.csv"},
    )


@router.get("/hotels/pdf")
async def export_hotels_pdf(
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    """Export hotels to PDF."""
    query = select(Hotel).where(Hotel.is_active)
    result = await db.execute(query)
    hotels = result.scalars().all()

    data = export_service.prepare_travel_data(hotels, "hotels")
    pdf_output = export_service.generate_pdf(data, "Hotels Report", "hotels.pdf")

    return Response(
        content=pdf_output.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=hotels.pdf"},
    )
