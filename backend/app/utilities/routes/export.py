"""Utilities export endpoints."""

from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_database_session
from app.core.models.user import User
from app.utilities.models import UtilityService
from app.utils.export import export_service

router = APIRouter(prefix="/api/utilities/export", tags=["Utilities Export"])


@router.get("/services/csv")
async def export_services_csv(
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    """Export utility services to CSV."""
    query = select(UtilityService).where(UtilityService.is_active)
    result = await db.execute(query)
    services = result.scalars().all()

    data = export_service.prepare_services_data(services)
    csv_output = export_service.generate_csv(data, "services.csv")

    return Response(
        content=csv_output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=services.csv"},
    )


@router.get("/services/pdf")
async def export_services_pdf(
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    """Export utility services to PDF."""
    query = select(UtilityService).where(UtilityService.is_active)
    result = await db.execute(query)
    services = result.scalars().all()

    data = export_service.prepare_services_data(services)
    pdf_output = export_service.generate_pdf(data, "Utility Services Report", "services.pdf")

    return Response(
        content=pdf_output.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=services.pdf"},
    )
