"""Real estate routes."""

from .alerts import router as alerts_router
from .deals import router as deals_router
from .properties import router as properties_router

__all__ = ["properties_router", "deals_router", "alerts_router"]
