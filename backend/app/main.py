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
from app.core.routes.notifications import router as notifications_router
from app.core.routes.scraping import router as scraping_router
from app.core.routes.status import router as status_router
from app.core.scheduler import scheduler_manager
from app.core.scraping.scraping_jobs import scraping_scheduler
from app.ecommerce.routes.analytics import router as analytics_router
from app.ecommerce.routes.deals import router as deals_router
from app.ecommerce.routes.deal_preferences import router as deal_preferences_router
from app.ecommerce.routes.export import router as ecommerce_export_router
from app.ecommerce.routes.price_analytics import router as price_analytics_router
from app.ecommerce.routes.product_search import router as product_search_router
from app.ecommerce.routes.products import router as products_router
from app.ecommerce.routes.watchlist import router as watchlist_router
from app.real_estate.routes import alerts_router
from app.real_estate.routes import deals_router as re_deals_router
from app.real_estate.routes import properties_router
from app.real_estate.routes.export import router as real_estate_export_router
from app.travel.routes.export import router as travel_export_router
from app.travel.routes.travel import router as travel_router
from app.utilities.routes import alerts_router as util_alerts_router
from app.utilities.routes import deals_router as util_deals_router
from app.utilities.routes import (
    services_router,
)
from app.utilities.routes.export import router as utilities_export_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    setup_logging()
    await scheduler_manager.start()
    await job_manager.register_all_jobs()
    scraping_scheduler.start()
    yield
    # Shutdown
    scraping_scheduler.stop()
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
app.include_router(notifications_router)
app.include_router(scraping_router)
app.include_router(products_router)
app.include_router(product_search_router)
app.include_router(deals_router)
app.include_router(deal_preferences_router)
app.include_router(price_analytics_router)
app.include_router(watchlist_router)
app.include_router(analytics_router)
app.include_router(travel_router)
app.include_router(properties_router)
app.include_router(re_deals_router)
app.include_router(alerts_router)
app.include_router(services_router)
app.include_router(util_deals_router)
app.include_router(util_alerts_router)
app.include_router(ecommerce_export_router)
app.include_router(travel_export_router)
app.include_router(real_estate_export_router)
app.include_router(utilities_export_router)
