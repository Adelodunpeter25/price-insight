"""E-commerce schemas."""

from .deal import (
    AlertHistoryResponse,
    AlertListResponse,
    AlertRuleCreate,
    AlertRuleResponse,
    DealListResponse,
    DealResponse,
    DealWithProductResponse,
)
from .product import (
    ProductCreate,
    ProductDetailResponse,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)

__all__ = [
    "ProductCreate",
    "ProductUpdate", 
    "ProductResponse",
    "ProductDetailResponse",
    "ProductListResponse",
    "DealResponse",
    "DealWithProductResponse",
    "DealListResponse",
    "AlertRuleCreate",
    "AlertRuleResponse",
    "AlertHistoryResponse",
    "AlertListResponse",
]