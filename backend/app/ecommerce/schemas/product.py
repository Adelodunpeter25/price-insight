"""Product schemas for API requests and responses."""

from decimal import Decimal
from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, HttpUrl


class ProductCreate(BaseModel):
    """Schema for creating a new product."""
    
    name: str
    url: HttpUrl
    site: str
    category: Optional[str] = None


class ProductUpdate(BaseModel):
    """Schema for updating a product."""
    
    name: Optional[str] = None
    category: Optional[str] = None
    is_tracked: Optional[bool] = None


class PriceHistoryResponse(BaseModel):
    """Schema for price history response."""
    
    id: int
    price: Decimal
    currency: str
    availability: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    """Schema for product response."""
    
    id: int
    name: str
    url: str
    site: str
    category: Optional[str]
    is_tracked: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProductDetailResponse(ProductResponse):
    """Schema for detailed product response with price history."""
    
    price_history: List[PriceHistoryResponse] = []


class ProductListResponse(BaseModel):
    """Schema for paginated product list response."""
    
    items: List[ProductResponse]
    total: int
    page: int
    size: int
    pages: int