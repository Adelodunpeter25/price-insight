"""Real estate export endpoints."""

from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_database_session
from app.core.models.user import User
from app.real_estate.models import Property
from app.utils.export import export_service

router = APIRouter(prefix="/api/real-estate/export", tags=["Real Estate Export"])


@router.get("/properties/csv")
async def export_properties_csv(
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    """Export properties to CSV."""
    query = select(Property).where(Property.is_active)
    result = await db.execute(query)
    properties = result.scalars().all()

    data = export_service.prepare_properties_data(properties)
    csv_output = export_service.generate_csv(data, "properties.csv")

    return Response(
        content=csv_output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=properties.csv"},
    )


@router.get("/properties/pdf")
async def export_properties_pdf(
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    """Export properties to PDF."""
    query = select(Property).where(Property.is_active)
    result = await db.execute(query)
    properties = result.scalars().all()

    data = export_service.prepare_properties_data(properties)
    pdf_output = export_service.generate_pdf(data, "Properties Report", "properties.pdf")

    return Response(
        content=pdf_output.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=properties.pdf"},
    )
