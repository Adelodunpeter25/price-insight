"""Status response schemas."""

from typing import List, Optional
from pydantic import BaseModel


class JobStatus(BaseModel):
    """Job status information."""
    
    id: str
    name: str
    next_run: Optional[str]
    trigger: str


class StatusResponse(BaseModel):
    """System status response schema."""
    
    scheduler_running: bool
    total_jobs: int
    jobs: List[JobStatus]