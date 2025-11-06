"""Monitoring endpoints for health and metrics."""

from fastapi import APIRouter

from app.core.monitoring import monitoring_service

router = APIRouter(prefix="/api/monitoring", tags=["Monitoring"])


@router.get("/health")
async def get_health():
    """Get application health status."""
    return monitoring_service.get_health_status()


@router.get("/metrics")
async def get_metrics():
    """Get detailed application metrics."""
    return monitoring_service.get_detailed_metrics()


@router.get("/performance")
async def get_performance_summary():
    """Get performance summary."""
    health = monitoring_service.get_health_status()
    return {
        "status": health["status"],
        "uptime_seconds": health["uptime_seconds"],
        "scraping_success_rate": health["scraping_success_rate"],
        "avg_response_time_ms": health["avg_response_time_ms"],
        "scheduler_running": health["scheduler_running"],
    }