"""Utility service management API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_database_session
from app.core.models.user import User
from app.utilities.models import UtilityService
from app.utilities.schemas.service import (
    UtilityServiceCreate,
    UtilityServiceDetailResponse,
    UtilityServiceListResponse,
    UtilityServiceResponse,
    UtilityServiceUpdate,
)
from app.utilities.services.utility_service import UtilityServiceManager
from app.utils.pagination import PaginationParams, paginate_query

router = APIRouter(prefix="/api/utilities/services", tags=["Utility Services"])


@router.post("/", response_model=UtilityServiceResponse, status_code=201)
async def create_service(
    service_data: UtilityServiceCreate,
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    """Add utility service to track."""
    service_manager = UtilityServiceManager(db)

    try:
        service = await service_manager.get_or_create_service(
            url=str(service_data.url),
            name=service_data.name,
            service_type=service_data.service_type,
            provider=service_data.provider,
            site=service_data.site,
            billing_type=service_data.billing_type,
            billing_cycle=service_data.billing_cycle,
            plan_details=service_data.plan_details,
        )
        return UtilityServiceResponse.model_validate(service)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create service: {str(e)}")


@router.get("/", response_model=UtilityServiceListResponse)
async def list_services(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    service_type: Optional[str] = Query(None, description="Filter by service type"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    billing_type: Optional[str] = Query(None, description="Filter by billing type"),
    is_tracked: Optional[bool] = Query(None, description="Filter by tracking status"),
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    """List tracked utility services with pagination and filters."""

    query = select(UtilityService).where(UtilityService.is_active)

    if service_type:
        query = query.where(UtilityService.service_type == service_type)
    if provider:
        query = query.where(UtilityService.provider.ilike(f"%{provider}%"))
    if billing_type:
        query = query.where(UtilityService.billing_type == billing_type)
    if is_tracked is not None:
        query = query.where(UtilityService.is_tracked == is_tracked)

    query = query.order_by(UtilityService.created_at.desc())

    pagination = PaginationParams(page=page, size=size)
    result = await paginate_query(db, query, pagination, UtilityServiceResponse)

    return UtilityServiceListResponse(**result.model_dump())


@router.get("/{service_id}", response_model=UtilityServiceDetailResponse)
async def get_service(
    service_id: int,
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    """Get service details with price history."""

    service_manager = UtilityServiceManager(db)
    service = await service_manager.get_service_with_history(service_id)

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    return UtilityServiceDetailResponse.model_validate(service)


@router.patch("/{service_id}", response_model=UtilityServiceResponse)
async def update_service(
    service_id: int,
    service_data: UtilityServiceUpdate,
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    """Update service information."""

    query = select(UtilityService).where(UtilityService.id == service_id, UtilityService.is_active)
    result = await db.execute(query)
    service = result.scalar_one_or_none()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # Update fields
    update_data = service_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(service, field, value)

    await db.commit()
    await db.refresh(service)

    return UtilityServiceResponse.model_validate(service)


@router.delete("/{service_id}", status_code=204)
async def delete_service(
    service_id: int,
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    """Stop tracking service (soft delete)."""

    query = select(UtilityService).where(UtilityService.id == service_id, UtilityService.is_active)
    result = await db.execute(query)
    service = result.scalar_one_or_none()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # Soft delete
    service.is_active = False
    service.is_tracked = False

    await db.commit()

    return None
