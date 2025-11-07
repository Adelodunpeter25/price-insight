"""Application configuration settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # App settings
    app_name: str = "Price Insight API"
    debug: bool = False
    version: str = "0.1.0"

    # Database
    database_url: str = ""

    # Redis
    redis_url: str = ""

    # JWT
    secret_key: str = ""
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    # Exchange Rate API
    exchange_rate_api_key: str = ""

    # Email service (Resend)
    resend_api_key: str = ""
    from_email: str = "noreply@priceinsight.ng"

    class Config:
        env_file = ".env"


settings = Settings()
