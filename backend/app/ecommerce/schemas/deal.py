"""Deal and alert schemas for API requests and responses."""

from decimal import Decimal
from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel


class DealResponse(BaseModel):
    """Schema for deal response."""
    
    id: int
    product_id: int
    original_price: Decimal
    deal_price: Decimal
    discount_percent: Decimal
    deal_type: str
    description: Optional[str]
    deal_start_date: Optional[datetime]
    deal_end_date: Optional[datetime]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class DealWithProductResponse(DealResponse):
    """Schema for deal response with product information."""
    
    product_name: str
    product_url: str
    product_site: str


class AlertRuleCreate(BaseModel):
    """Schema for creating alert rules."""
    
    product_id: int
    rule_type: str  # price_drop, threshold, deal_appeared
    threshold_value: Optional[Decimal] = None
    percentage_threshold: Optional[Decimal] = None
    notification_method: str = "console"


class AlertRuleResponse(BaseModel):
    """Schema for alert rule response."""
    
    id: int
    product_id: int
    rule_type: str
    threshold_value: Optional[Decimal]
    percentage_threshold: Optional[Decimal]
    notification_method: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class AlertHistoryResponse(BaseModel):
    """Schema for alert history response."""
    
    id: int
    alert_rule_id: int
    product_id: int
    trigger_value: Decimal
    message: str
    notification_sent: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class AlertHistoryWithDetailsResponse(AlertHistoryResponse):
    """Schema for alert history with product and rule details."""
    
    product_name: str
    rule_type: str


class DealListResponse(BaseModel):
    """Schema for paginated deal list response."""
    
    items: List[DealWithProductResponse]
    total: int
    page: int
    size: int
    pages: int


class AlertListResponse(BaseModel):
    """Schema for paginated alert list response."""
    
    items: List[AlertHistoryWithDetailsResponse]
    total: int
    page: int
    size: int
    pages: int