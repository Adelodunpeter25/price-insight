"""Scraping management API endpoints."""

from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.models.user import User
from app.core.scraping.scraper_manager import scraper_manager
from app.core.scraping.scraping_jobs import scraping_scheduler
from app.core.scraping.scraper_factory import scraper_factory

router = APIRouter(prefix="/scraping", tags=["Scraping"])


@router.post("/scrape-url")
async def scrape_single_url(
    url: str,
    category: str = "auto",
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Scrape a single URL and return extracted data."""
    try:
        result = await scraper_manager.scrape_url(url, category)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to scrape URL")
        
        return {
            "success": True,
            "data": result,
            "message": "URL scraped successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


@router.post("/scrape-category/{category}")
async def scrape_category(
    category: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Trigger scraping for a specific category."""
    valid_categories = ["ecommerce", "travel", "real_estate", "utilities", "all"]
    
    if category not in valid_categories:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid category. Must be one of: {valid_categories}"
        )
    
    # Trigger manual scraping in background
    scraping_scheduler.trigger_manual_scrape(category)
    
    return {
        "success": True,
        "message": f"Scraping job for '{category}' category has been queued",
        "category": category
    }


@router.get("/status")
async def get_scraping_status(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get status of scraping scheduler and jobs."""
    return scraping_scheduler.get_job_status()


@router.post("/scheduler/start")
async def start_scheduler(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Start the scraping scheduler."""
    try:
        scraping_scheduler.start()
        return {
            "success": True,
            "message": "Scraping scheduler started successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start scheduler: {str(e)}")


@router.post("/scheduler/stop")
async def stop_scheduler(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Stop the scraping scheduler."""
    try:
        scraping_scheduler.stop()
        return {
            "success": True,
            "message": "Scraping scheduler stopped successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop scheduler: {str(e)}")


@router.get("/supported-sites")
async def get_supported_sites() -> Dict[str, Any]:
    """Get list of supported sites for scraping."""
    factory = scraper_factory
    
    return {
        "ecommerce_sites": list(factory.ecommerce_sites.keys()),
        "travel_sites": list(factory.travel_sites.keys()),
        "real_estate_sites": list(factory.real_estate_sites.keys()),
        "utility_sites": list(factory.utility_sites.keys()),
        "message": "Sites with specific scrapers. Generic scraping available for other sites."
    }