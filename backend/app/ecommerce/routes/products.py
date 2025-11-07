"""Product management API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_database_session
from app.ecommerce.models import Product
from app.ecommerce.schemas.product import (
    ProductCreate,
    ProductDetailResponse,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from app.ecommerce.services.product_service import ProductService
from app.utils.pagination import PaginationParams, paginate_query

router = APIRouter(prefix="/api/e-commerce/products", tags=["E-commerce Products"])


@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    product_data: ProductCreate, db: AsyncSession = Depends(get_database_session)
):
    """Add a new product to track."""

    product_service = ProductService(db)

    try:
        product = await product_service.get_or_create_product(
            url=str(product_data.url),
            name=product_data.name,
            site=product_data.site,
            category=product_data.category,
        )
        return ProductResponse.model_validate(product)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create product: {str(e)}")


@router.get("/", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    site: Optional[str] = Query(None, description="Filter by site"),
    category: Optional[str] = Query(None, description="Filter by category"),
    is_tracked: Optional[bool] = Query(None, description="Filter by tracking status"),
    db: AsyncSession = Depends(get_database_session),
):
    """List tracked products with pagination and filters."""

    # Build query with filters
    query = select(Product).where(Product.is_active == True)

    if site:
        query = query.where(Product.site.ilike(f"%{site}%"))
    if category:
        query = query.where(Product.category.ilike(f"%{category}%"))
    if is_tracked is not None:
        query = query.where(Product.is_tracked == is_tracked)

    # Order by creation date
    query = query.order_by(Product.created_at.desc())

    # Use pagination utility
    pagination = PaginationParams(page=page, size=size)
    result = await paginate_query(db, query, pagination, ProductResponse)

    return ProductListResponse(**result.model_dump())


@router.get("/{product_id}", response_model=ProductDetailResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_database_session)):
    """Get product details with price history."""

    query = (
        select(Product)
        .options(selectinload(Product.price_history))
        .where(Product.id == product_id, Product.is_active == True)
    )

    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return ProductDetailResponse.model_validate(product)


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int, product_data: ProductUpdate, db: AsyncSession = Depends(get_database_session)
):
    """Update product information."""

    # Get product
    query = select(Product).where(Product.id == product_id, Product.is_active == True)
    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Update fields
    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)

    return ProductResponse.model_validate(product)


@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_database_session)):
    """Stop tracking a product (soft delete)."""

    # Get product
    query = select(Product).where(Product.id == product_id, Product.is_active == True)
    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Soft delete
    product.is_active = False
    product.is_tracked = False

    await db.commit()

    return None
