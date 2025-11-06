"""Deal and alert API endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.deps import get_database_session
from app.core.models.alert import AlertHistory, AlertRule
from app.ecommerce.models import Deal, Product
from app.ecommerce.schemas.deal import (
    AlertHistoryWithDetailsResponse,
    AlertListResponse,
    AlertRuleCreate,
    AlertRuleResponse,
    DealListResponse,
    DealResponse,
    DealWithProductResponse,
)
from app.core.alerts.rules_engine import AlertRulesEngine

router = APIRouter(prefix="/api", tags=["Deals & Alerts"])


@router.get("/deals", response_model=DealListResponse)
async def list_deals(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    site: Optional[str] = Query(None, description="Filter by site"),
    min_discount: Optional[float] = Query(None, ge=0, le=100, description="Minimum discount percentage"),
    active_only: bool = Query(True, description="Show only active deals"),
    db: AsyncSession = Depends(get_database_session)
):
    """List deals with pagination and filters."""
    
    # Build query with joins
    query = (
        select(Deal, Product.name, Product.url, Product.site)
        .join(Product, Deal.product_id == Product.id)
        .where(Product.is_active == True)
    )
    
    if active_only:
        query = query.where(Deal.is_active == True)
    if site:
        query = query.where(Product.site.ilike(f"%{site}%"))
    if min_discount:
        query = query.where(Deal.discount_percent >= min_discount)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(Deal.created_at.desc())
    
    # Execute query
    result = await db.execute(query)
    deals_data = result.all()
    
    # Format response
    deals = []
    for deal, product_name, product_url, product_site in deals_data:
        deal_dict = DealResponse.model_validate(deal).model_dump()
        deal_dict.update({
            "product_name": product_name,
            "product_url": product_url,
            "product_site": product_site
        })
        deals.append(DealWithProductResponse(**deal_dict))
    
    # Calculate pagination info
    pages = (total + size - 1) // size
    
    return DealListResponse(
        items=deals,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/deals/{deal_id}", response_model=DealResponse)
async def get_deal(
    deal_id: int,
    db: AsyncSession = Depends(get_database_session)
):
    """Get deal details."""
    
    query = select(Deal).where(Deal.id == deal_id, Deal.is_active == True)
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
    db: AsyncSession = Depends(get_database_session)
):
    """List alert history with pagination and filters."""
    
    # Build query with joins
    query = (
        select(AlertHistory, Product.name, AlertRule.rule_type)
        .join(Product, AlertHistory.product_id == Product.id)
        .join(AlertRule, AlertHistory.alert_rule_id == AlertRule.id)
        .where(Product.is_active == True)
    )
    
    if product_id:
        query = query.where(AlertHistory.product_id == product_id)
    if rule_type:
        query = query.where(AlertRule.rule_type == rule_type)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(AlertHistory.created_at.desc())
    
    # Execute query
    result = await db.execute(query)
    alerts_data = result.all()
    
    # Format response
    alerts = []
    for alert, product_name, rule_type in alerts_data:
        alert_dict = AlertHistoryResponse.model_validate(alert).model_dump()
        alert_dict.update({
            "product_name": product_name,
            "rule_type": rule_type
        })
        alerts.append(AlertHistoryWithDetailsResponse(**alert_dict))
    
    # Calculate pagination info
    pages = (total + size - 1) // size
    
    return AlertListResponse(
        items=alerts,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.post("/alerts/rules", response_model=AlertRuleResponse, status_code=201)
async def create_alert_rule(
    rule_data: AlertRuleCreate,
    db: AsyncSession = Depends(get_database_session)
):
    """Create a new alert rule."""
    
    # Validate product exists
    product_query = select(Product).where(
        Product.id == rule_data.product_id,
        Product.is_active == True
    )
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
            notification_method=rule_data.notification_method
        )
        
        return AlertRuleResponse.model_validate(rule)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create alert rule: {str(e)}")


@router.get("/alerts/rules", response_model=List[AlertRuleResponse])
async def list_alert_rules(
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    db: AsyncSession = Depends(get_database_session)
):
    """List alert rules."""
    
    query = select(AlertRule).where(AlertRule.is_active == True)
    
    if product_id:
        query = query.where(AlertRule.product_id == product_id)
    
    query = query.order_by(AlertRule.created_at.desc())
    
    result = await db.execute(query)
    rules = list(result.scalars().all())
    
    return [AlertRuleResponse.model_validate(rule) for rule in rules]