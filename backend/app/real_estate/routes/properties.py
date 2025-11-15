"""Property management API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import invalidate_cache
from app.core.deps import get_current_user, get_database_session
from app.core.models.user import User
from app.real_estate.models import Property
from app.real_estate.schemas.property import (
    PropertyCreate,
    PropertyDetailResponse,
    PropertyListResponse,
    PropertyResponse,
    PropertyUpdate,
)
from app.real_estate.services.property_service import PropertyService
from app.utils.pagination import PaginationParams, paginate_query

router = APIRouter(prefix="/api/real-estate/properties", tags=["Real Estate Properties"])


@router.post("/", response_model=PropertyResponse, status_code=201)
async def create_property(
    property_data: PropertyCreate,
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    """Add property to track."""
    property_service = PropertyService(db)

    try:
        property_obj = await property_service.get_or_create_property(
            url=str(property_data.url),
            name=property_data.name,
            property_type=property_data.property_type,
            location=property_data.location,
            site=property_data.site,
            listing_type=property_data.listing_type,
            bedrooms=property_data.bedrooms,
            bathrooms=property_data.bathrooms,
            size_sqm=property_data.size_sqm,
            features=property_data.features,
        )
        invalidate_cache("property_analytics")
        invalidate_cache("property_dashboard")
        return PropertyResponse.model_validate(property_obj)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create property: {str(e)}")


@router.get("/", response_model=PropertyListResponse)
async def list_properties(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    property_type: Optional[str] = Query(None, description="Filter by property type"),
    location: Optional[str] = Query(None, description="Filter by location"),
    listing_type: Optional[str] = Query(None, description="Filter by listing type"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    is_tracked: Optional[bool] = Query(None, description="Filter by tracking status"),
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    """List tracked properties with pagination and filters."""

    query = select(Property).where(Property.is_active)

    if property_type:
        query = query.where(Property.property_type.ilike(f"%{property_type}%"))
    if location:
        query = query.where(Property.location.ilike(f"%{location}%"))
    if listing_type:
        query = query.where(Property.listing_type == listing_type)
    if min_price:
        query = query.where(Property.price >= min_price)
    if max_price:
        query = query.where(Property.price <= max_price)
    if is_tracked is not None:
        query = query.where(Property.is_tracked == is_tracked)

    query = query.order_by(Property.created_at.desc())

    pagination = PaginationParams(page=page, size=size)
    result = await paginate_query(db, query, pagination, PropertyResponse)

    return PropertyListResponse(**result.model_dump())


@router.get("/{property_id}", response_model=PropertyDetailResponse)
async def get_property(
    property_id: int,
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    """Get property details with price history."""

    property_service = PropertyService(db)
    property_obj = await property_service.get_property_with_history(property_id)

    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")

    return PropertyDetailResponse.model_validate(property_obj)


@router.patch("/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: int,
    property_data: PropertyUpdate,
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    """Update property information."""

    query = select(Property).where(Property.id == property_id, Property.is_active)
    result = await db.execute(query)
    property_obj = result.scalar_one_or_none()

    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")

    # Update fields
    update_data = property_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(property_obj, field, value)

    await db.commit()
    await db.refresh(property_obj)
    
    invalidate_cache("property_analytics")
    invalidate_cache("property_price")

    return PropertyResponse.model_validate(property_obj)


@router.delete("/{property_id}", status_code=204)
async def delete_property(
    property_id: int,
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    """Stop tracking property (soft delete)."""

    query = select(Property).where(Property.id == property_id, Property.is_active)
    result = await db.execute(query)
    property_obj = result.scalar_one_or_none()

    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")

    # Soft delete
    property_obj.is_active = False
    property_obj.is_tracked = False

    await db.commit()
    
    invalidate_cache("property_analytics")
    invalidate_cache("property_dashboard")

    return None
