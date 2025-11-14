"""Database configuration and session management."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# Create async engine with optimized connection pooling
engine = create_async_engine(
    settings.database_url,
    pool_size=20,  # Base connection pool size
    max_overflow=10,  # Allow 10 additional connections under load
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_timeout=30,  # Wait 30s for connection from pool
    echo_pool=False,  # Disable pool logging
)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
