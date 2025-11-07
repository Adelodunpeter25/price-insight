"""Utility price history model."""

from decimal import Decimal

from sqlalchemy import DECIMAL, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.base import BaseModel


class UtilityPriceHistory(BaseModel):
    """Utility price history model."""

    __tablename__ = "utility_price_history"

    service_id: Mapped[int] = mapped_column(
        ForeignKey("utility_services.id"), nullable=False, index=True
    )
    price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="NGN")
    tariff_details: Mapped[str] = mapped_column(String(200), nullable=True)
    source: Mapped[str] = mapped_column(String(100), default="scraper")

    # Relationships
    service = relationship("UtilityService", back_populates="price_history")

    def __repr__(self) -> str:
        """String representation."""
        return f"<UtilityPriceHistory(service_id={self.service_id}, price=₦{self.price})>"
