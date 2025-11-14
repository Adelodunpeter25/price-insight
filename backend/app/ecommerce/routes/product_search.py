"""Product search API endpoints."""

import logging
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.models.user import User
from app.ecommerce.models.product import Product
from app.ecommerce.services.product_search import ProductSearchService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products/search", tags=["Product Search"])


@router.get("/tracked")
def search_tracked_products(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search existing tracked products."""
    products = ProductSearchService.search_tracked_products(db, q, limit)
    
    return {
        "query": q,
        "count": len(products),
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "url": p.url,
                "site": p.site,
                "category": p.category
            }
            for p in products
        ]
    }


@router.post("/scrape")
async def scrape_product_from_url(
    url: str = Query(..., description="Product URL to scrape"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Scrape product from URL and add to database."""
    product = await ProductSearchService.scrape_product_from_url(db, url)
    
    if not product:
        return {
            "success": False,
            "message": "Failed to scrape product from URL"
        }
    
    return {
        "success": True,
        "product": {
            "id": product.id,
            "name": product.name,
            "url": product.url,
            "site": product.site
        }
    }


@router.get("/discover")
async def discover_products(
    q: str = Query(..., min_length=2, description="Product name to search"),
    max_results: int = Query(5, ge=1, le=10),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search and scrape products from multiple e-commerce sites."""
    products = await ProductSearchService.search_and_scrape_products(db, q, max_results)
    
    return {
        "query": q,
        "count": len(products),
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "url": p.url,
                "site": p.site
            }
            for p in products
        ]
    }
