"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine
from app.core.job_manager import job_manager
from app.core.logging import setup_logging
from app.core.routes.auth import router as auth_router
from app.core.routes.health import router as health_router
from app.core.routes.monitoring import router as monitoring_router
from app.core.routes.status import router as status_router
from app.core.scheduler import scheduler_manager
from app.ecommerce.routes.deals import router as deals_router
from app.ecommerce.routes.products import router as products_router
from app.travel.routes.travel import router as travel_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    setup_logging()
    await scheduler_manager.start()
    await job_manager.register_all_jobs()
    yield
    # Shutdown
    await scheduler_manager.shutdown()
    await engine.dispose()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Multi-category deal aggregation and price tracking platform",
    lifespan=lifespan,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(health_router)
app.include_router(status_router)
app.include_router(monitoring_router)
app.include_router(products_router)
app.include_router(deals_router)
app.include_router(travel_router)
