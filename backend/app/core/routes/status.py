"""Status endpoints for monitoring jobs and system health."""

from fastapi import APIRouter

from app.core.job_manager import job_manager
from app.core.scheduler import scheduler_manager
from app.core.schemas.status import StatusResponse

router = APIRouter()


@router.get("/api/status", response_model=StatusResponse)
async def get_system_status():
    """Get system status including scheduler and job information."""
    
    job_status = job_manager.get_job_status()
    
    return StatusResponse(
        scheduler_running=scheduler_manager.is_running,
        total_jobs=len(job_status),
        jobs=job_status
    )