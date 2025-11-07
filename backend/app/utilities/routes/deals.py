"""Utility deal API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_database_session
from app.core.models.user import User
from app.utilities.models import UtilityDeal
from app.utilities.schemas.deal import (
    UtilityDealListResponse,
    UtilityDealResponse,
)
from app.utils.pagination import PaginationParams, paginate_query

router = APIRouter(prefix="/api/utilities/deals", tags=["Utility Deals"])


@router.get("/", response_model=UtilityDealListResponse)
async def list_deals(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    deal_type: Optional[str] = Query(None, description="Filter by deal type"),
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    """List active utility deals."""

    query = select(UtilityDeal).where(UtilityDeal.is_active)

    if deal_type:
        query = query.where(UtilityDeal.deal_type == deal_type)

    query = query.order_by(UtilityDeal.created_at.desc())

    pagination = PaginationParams(page=page, size=size)
    result = await paginate_query(db, query, pagination, UtilityDealResponse)

    return UtilityDealListResponse(**result.model_dump())


@router.get("/{deal_id}", response_model=UtilityDealResponse)
async def get_deal(
    deal_id: int,
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    """Get deal details."""

    query = select(UtilityDeal).where(UtilityDeal.id == deal_id, UtilityDeal.is_active)
    result = await db.execute(query)
    deal = result.scalar_one_or_none()

    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    return UtilityDealResponse.model_validate(deal)
