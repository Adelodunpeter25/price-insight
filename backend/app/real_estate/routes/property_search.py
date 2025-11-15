"""Property search API endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.models.user import User
from app.real_estate.schemas.property import PropertyResponse
from app.real_estate.services.property_search import PropertySearchService

router = APIRouter(prefix="/api/real-estate/properties/search", tags=["Real Estate Search"])


@router.get("/tracked", response_model=List[PropertyResponse])
def search_tracked_properties(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search existing tracked properties."""
    properties = PropertySearchService.search_tracked_properties(db, q, limit)
    return [PropertyResponse.model_validate(p) for p in properties]


@router.post("/scrape")
async def scrape_property_from_url(
    url: str = Query(..., description="Property URL to scrape"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Scrape property from URL."""
    if not PropertySearchService.validate_url(url):
        raise HTTPException(status_code=400, detail="Invalid URL")

    property_obj = await PropertySearchService.scrape_property_from_url(db, url)

    if not property_obj:
        raise HTTPException(status_code=400, detail="Failed to scrape property")

    return PropertyResponse.model_validate(property_obj)


@router.get("/discover")
async def discover_properties(
    q: str = Query(..., min_length=2, description="Property search query"),
    max_results: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Discover properties from multiple sites."""
    properties = await PropertySearchService.search_and_scrape_properties(db, q, max_results)

    return {
        "query": q,
        "count": len(properties),
        "properties": [PropertyResponse.model_validate(p) for p in properties],
    }
