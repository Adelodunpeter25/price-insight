"""Utilities routes."""

from .alerts import router as alerts_router
from .deals import router as deals_router
from .services import router as services_router

__all__ = ["services_router", "deals_router", "alerts_router"]
