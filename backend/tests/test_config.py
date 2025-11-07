"""Test configuration and base test class."""

import asyncio
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db

# Import all models to ensure they're registered
from app.core.models.alert import AlertHistory, AlertRule  # noqa: F401
from app.core.models.base import Base
from app.ecommerce.models.deal import Deal  # noqa: F401
from app.ecommerce.models.price_history import PriceHistory  # noqa: F401
from app.ecommerce.models.product import Product  # noqa: F401
from app.main import app

# Test database URL (SQLite in memory)
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
SYNC_DATABASE_URL = "sqlite:///./test.db"

# Create sync engine for table creation
sync_engine = create_engine(
    SYNC_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create async engine for tests
async_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)

# Create all tables using sync engine
Base.metadata.create_all(bind=sync_engine)


async def override_get_db():
    """Override database dependency for testing."""
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


class BaseTestCase(unittest.TestCase):
    """Base test case with common setup."""

    def setUp(self):
        """Set up test client and database session."""
        self.client = TestClient(app)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        """Clean up after test."""
        self.loop.close()
