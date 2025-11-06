"""Deal and alert API endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.alerts.rules_engine import AlertRulesEngine
from app.core.deps import get_database_session
from app.core.models.alert import AlertHistory, AlertRule
from app.ecommerce.models import Deal, Product
from app.ecommerce.schemas.deal import (
    AlertHistoryResponse,
    AlertHistoryWithDetailsResponse,
    AlertListResponse,
    AlertRuleCreate,
    AlertRuleResponse,
    DealListResponse,
    DealResponse,
    DealWithProductResponse,
)
from app.utils.pagination import PaginationParams, paginate_joined_query

router = APIRouter(prefix="/api", tags=["Deals & Alerts"])


@router.get("/deals", response_model=DealListResponse)
async def list_deals(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    site: Optional[str] = Query(None, description="Filter by site"),
    min_discount: Optional[float] = Query(
        None, ge=0, le=100, description="Minimum discount percentage"
    ),
    active_only: bool = Query(True, description="Show only active deals"),
    db: AsyncSession = Depends(get_database_session),
):
    """List deals with pagination and filters."""

    # Build query with joins
    query = (
        select(Deal, Product.name, Product.url, Product.site)
        .join(Product, Deal.product_id == Product.id)
        .where(Product.is_active)
    )

    if active_only:
        query = query.where(Deal.is_active)
    if site:
        query = query.where(Product.site.ilike(f"%{site}%"))
    if min_discount:
        query = query.where(Deal.discount_percent >= min_discount)

    # Order by creation date
    query = query.order_by(Deal.created_at.desc())

    # Format function for joined query results
    def format_deal(row):
        deal, product_name, product_url, product_site = row
        deal_dict = DealResponse.model_validate(deal).model_dump()
        deal_dict.update(
            {"product_name": product_name, "product_url": product_url, "product_site": product_site}
        )
        return DealWithProductResponse(**deal_dict)

    # Use pagination utility
    pagination = PaginationParams(page=page, size=size)
    result = await paginate_joined_query(db, query, pagination, format_deal)

    return DealListResponse(**result.model_dump())


@router.get("/deals/{deal_id}", response_model=DealResponse)
async def get_deal(deal_id: int, db: AsyncSession = Depends(get_database_session)):
    """Get deal details."""

    query = select(Deal).where(Deal.id == deal_id, Deal.is_active)
    result = await db.execute(query)
    deal = result.scalar_one_or_none()

    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    return DealResponse.model_validate(deal)


@router.get("/alerts", response_model=AlertListResponse)
async def list_alerts(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    rule_type: Optional[str] = Query(None, description="Filter by rule type"),
    db: AsyncSession = Depends(get_database_session),
):
    """List alert history with pagination and filters."""

    # Build query with joins
    query = (
        select(AlertHistory, Product.name, AlertRule.rule_type)
        .join(Product, AlertHistory.product_id == Product.id)
        .join(AlertRule, AlertHistory.alert_rule_id == AlertRule.id)
        .where(Product.is_active)
    )

    if product_id:
        query = query.where(AlertHistory.product_id == product_id)
    if rule_type:
        query = query.where(AlertRule.rule_type == rule_type)

    # Order by creation date
    query = query.order_by(AlertHistory.created_at.desc())

    # Format function for joined query results
    def format_alert(row):
        alert, product_name, rule_type = row
        alert_dict = AlertHistoryResponse.model_validate(alert).model_dump()
        alert_dict.update({"product_name": product_name, "rule_type": rule_type})
        return AlertHistoryWithDetailsResponse(**alert_dict)

    # Use pagination utility
    pagination = PaginationParams(page=page, size=size)
    result = await paginate_joined_query(db, query, pagination, format_alert)

    return AlertListResponse(**result.model_dump())


@router.post("/alerts/rules", response_model=AlertRuleResponse, status_code=201)
async def create_alert_rule(
    rule_data: AlertRuleCreate, db: AsyncSession = Depends(get_database_session)
):
    """Create a new alert rule."""

    # Validate product exists
    product_query = select(Product).where(Product.id == rule_data.product_id, Product.is_active)
    product_result = await db.execute(product_query)
    product = product_result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Create alert rule
    rules_engine = AlertRulesEngine(db)

    try:
        rule = await rules_engine.create_alert_rule(
            product_id=rule_data.product_id,
            rule_type=rule_data.rule_type,
            threshold_value=rule_data.threshold_value,
            percentage_threshold=rule_data.percentage_threshold,
            notification_method=rule_data.notification_method,
        )

        return AlertRuleResponse.model_validate(rule)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create alert rule: {str(e)}")


@router.get("/alerts/rules", response_model=List[AlertRuleResponse])
async def list_alert_rules(
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    db: AsyncSession = Depends(get_database_session),
):
    """List alert rules."""

    query = select(AlertRule).where(AlertRule.is_active)

    if product_id:
        query = query.where(AlertRule.product_id == product_id)

    query = query.order_by(AlertRule.created_at.desc())

    result = await db.execute(query)
    rules = list(result.scalars().all())

    return [AlertRuleResponse.model_validate(rule) for rule in rules]
