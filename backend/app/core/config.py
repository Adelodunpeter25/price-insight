"""Application configuration settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # App settings
    app_name: str = "Price Insight API"
    debug: bool = False
    version: str = "0.1.0"
    
    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost/price_insight"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # API settings
    api_v1_prefix: str = "/api/v1"
    
    class Config:
        env_file = ".env"


settings = Settings()