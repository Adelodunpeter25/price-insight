"""Scraping management API endpoints."""

from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.models.user import User
from app.core.scraping.scraper_factory import scraper_factory
from app.core.scraping.scraper_manager import scraper_manager
from app.core.scraping.scraping_jobs import scraping_scheduler
from app.core.tasks.scraping_tasks import (
    scrape_all_ecommerce,
    scrape_all_real_estate,
    scrape_all_travel,
    scrape_all_utilities,
)

router = APIRouter(prefix="/scraping", tags=["Scraping"])


@router.post("/scrape-url")
async def scrape_single_url(
    url: str, category: str = "auto", current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Scrape a single URL and return extracted data."""
    try:
        result = await scraper_manager.scrape_url(url, category)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to scrape URL")

        return {"success": True, "data": result, "message": "URL scraped successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


@router.post("/scrape-category/{category}")
async def scrape_category(
    category: str,
    distributed: bool = True,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Trigger scraping for a specific category."""
    valid_categories = ["ecommerce", "travel", "real_estate", "utilities", "all"]

    if category not in valid_categories:
        raise HTTPException(
            status_code=400, detail=f"Invalid category. Must be one of: {valid_categories}"
        )

    if distributed:
        # Use distributed Celery tasks
        task_map = {
            "ecommerce": scrape_all_ecommerce,
            "travel": scrape_all_travel,
            "real_estate": scrape_all_real_estate,
            "utilities": scrape_all_utilities,
        }
        
        if category == "all":
            tasks = [task.delay() for task in task_map.values()]
            return {
                "success": True,
                "message": "Distributed scraping started for all categories",
                "task_ids": [t.id for t in tasks],
                "mode": "distributed"
            }
        
        task = task_map[category].delay()
        return {
            "success": True,
            "message": f"Distributed scraping started for '{category}'",
            "task_id": task.id,
            "mode": "distributed"
        }
    else:
        # Use original scheduler method
        scraping_scheduler.trigger_manual_scrape(category)
        return {
            "success": True,
            "message": f"Scraping job for '{category}' category has been queued",
            "category": category,
            "mode": "scheduler"
        }


@router.get("/status")
async def get_scraping_status(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """Get status of scraping scheduler and jobs."""
    return scraping_scheduler.get_job_status()


@router.post("/scheduler/start")
async def start_scheduler(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """Start the scraping scheduler."""
    try:
        scraping_scheduler.start()
        return {"success": True, "message": "Scraping scheduler started successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start scheduler: {str(e)}")


@router.post("/scheduler/stop")
async def stop_scheduler(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """Stop the scraping scheduler."""
    try:
        scraping_scheduler.stop()
        return {"success": True, "message": "Scraping scheduler stopped successfully"}
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
        "message": "Sites with specific scrapers. Generic scraping available for other sites.",
    }


@router.get("/task/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get status of distributed scraping task."""
    from celery.result import AsyncResult
    
    task = AsyncResult(task_id)
    
    return {
        "task_id": task_id,
        "status": task.state,
        "result": task.result if task.ready() else None,
        "info": task.info
    }
