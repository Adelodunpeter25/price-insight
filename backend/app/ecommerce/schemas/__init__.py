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
from .deal_preference import (
    DealPreferenceCreate,
    DealPreferenceResponse,
    DealPreferenceUpdate,
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
    "DealPreferenceCreate",
    "DealPreferenceUpdate",
    "DealPreferenceResponse",
    "AlertRuleCreate",
    "AlertRuleResponse",
    "AlertHistoryResponse",
    "AlertListResponse",
]
