"""E-commerce export endpoints."""

from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_database_session
from app.core.models.user import User
from app.ecommerce.models import Product
from app.utils.export import export_service

router = APIRouter(prefix="/api/e-commerce/export", tags=["E-commerce Export"])


@router.get("/products/csv")
async def export_products_csv(
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    """Export products to CSV."""
    query = select(Product).where(Product.is_active == True)
    result = await db.execute(query)
    products = result.scalars().all()

    data = export_service.prepare_products_data(products)
    csv_output = export_service.generate_csv(data, "products.csv")

    return Response(
        content=csv_output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=products.csv"},
    )


@router.get("/products/pdf")
async def export_products_pdf(
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    """Export products to PDF."""
    query = select(Product).where(Product.is_active == True)
    result = await db.execute(query)
    products = result.scalars().all()

    data = export_service.prepare_products_data(products)
    pdf_output = export_service.generate_pdf(data, "Products Report", "products.pdf")

    return Response(
        content=pdf_output.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=products.pdf"},
    )
