"""Property alert API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_database_session
from app.core.models.user import User
from app.real_estate.models import PropertyAlertRule
from app.real_estate.schemas.alert import (
    PropertyAlertListResponse,
    PropertyAlertRuleCreate,
    PropertyAlertRuleResponse,
)
from app.utils.pagination import PaginationParams, paginate_query

router = APIRouter(prefix="/api/real-estate/alerts", tags=["Real Estate Alerts"])


@router.post("/rules", response_model=PropertyAlertRuleResponse, status_code=201)
async def create_alert_rule(
    alert_data: PropertyAlertRuleCreate,
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    """Create property alert rule."""
    
    alert_rule = PropertyAlertRule(
        property_id=alert_data.property_id,
        location=alert_data.location,
        property_type=alert_data.property_type,
        max_price=alert_data.max_price,
        min_bedrooms=alert_data.min_bedrooms,
        rule_type=alert_data.rule_type,
        threshold_value=alert_data.threshold_value,
        percentage_threshold=alert_data.percentage_threshold,
        notification_method=alert_data.notification_method,
    )

    db.add(alert_rule)
    await db.commit()
    await db.refresh(alert_rule)

    return PropertyAlertRuleResponse.model_validate(alert_rule)


@router.get("/", response_model=PropertyAlertListResponse)
async def list_alerts(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    """List property alerts."""
    
    query = select(PropertyAlertRule).where(PropertyAlertRule.is_active == True)
    query = query.order_by(PropertyAlertRule.created_at.desc())

    pagination = PaginationParams(page=page, size=size)
    result = await paginate_query(db, query, pagination, PropertyAlertRuleResponse)

    return PropertyAlertListResponse(**result.model_dump())