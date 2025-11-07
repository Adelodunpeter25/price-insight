"""Utility alert API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_database_session
from app.core.models.user import User
from app.utilities.models import UtilityAlertRule
from app.utilities.schemas.alert import (
    UtilityAlertListResponse,
    UtilityAlertRuleCreate,
    UtilityAlertRuleResponse,
)
from app.utils.pagination import PaginationParams, paginate_query

router = APIRouter(prefix="/api/utilities/alerts", tags=["Utility Alerts"])


@router.post("/rules", response_model=UtilityAlertRuleResponse, status_code=201)
async def create_alert_rule(
    alert_data: UtilityAlertRuleCreate,
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    """Create utility alert rule."""

    alert_rule = UtilityAlertRule(
        service_id=alert_data.service_id,
        service_type=alert_data.service_type,
        provider=alert_data.provider,
        max_price=alert_data.max_price,
        rule_type=alert_data.rule_type,
        threshold_value=alert_data.threshold_value,
        percentage_threshold=alert_data.percentage_threshold,
        notification_method=alert_data.notification_method,
    )

    db.add(alert_rule)
    await db.commit()
    await db.refresh(alert_rule)

    return UtilityAlertRuleResponse.model_validate(alert_rule)


@router.get("/", response_model=UtilityAlertListResponse)
async def list_alerts(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    """List utility alerts."""

    query = select(UtilityAlertRule).where(UtilityAlertRule.is_active)
    query = query.order_by(UtilityAlertRule.created_at.desc())

    pagination = PaginationParams(page=page, size=size)
    result = await paginate_query(db, query, pagination, UtilityAlertRuleResponse)

    return UtilityAlertListResponse(**result.model_dump())
