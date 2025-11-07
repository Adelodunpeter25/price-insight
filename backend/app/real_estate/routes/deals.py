"""Property deal API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_database_session
from app.core.models.user import User
from app.real_estate.models import PropertyDeal
from app.real_estate.schemas.deal import (
    PropertyDealListResponse,
    PropertyDealResponse,
)
from app.utils.pagination import PaginationParams, paginate_query

router = APIRouter(prefix="/api/real-estate/deals", tags=["Real Estate Deals"])


@router.get("/", response_model=PropertyDealListResponse)
async def list_deals(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    deal_type: Optional[str] = Query(None, description="Filter by deal type"),
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    """List active property deals."""

    query = select(PropertyDeal).where(PropertyDeal.is_active)

    if deal_type:
        query = query.where(PropertyDeal.deal_type == deal_type)

    query = query.order_by(PropertyDeal.created_at.desc())

    pagination = PaginationParams(page=page, size=size)
    result = await paginate_query(db, query, pagination, PropertyDealResponse)

    return PropertyDealListResponse(**result.model_dump())


@router.get("/{deal_id}", response_model=PropertyDealResponse)
async def get_deal(
    deal_id: int,
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    """Get deal details."""

    query = select(PropertyDeal).where(PropertyDeal.id == deal_id, PropertyDeal.is_active)
    result = await db.execute(query)
    deal = result.scalar_one_or_none()

    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    return PropertyDealResponse.model_validate(deal)
