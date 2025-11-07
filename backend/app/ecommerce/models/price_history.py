"""Price history model for tracking price changes."""

from decimal import Decimal

from sqlalchemy import DECIMAL, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.base import BaseModel


class PriceHistory(BaseModel):
    """Price history model for tracking price changes over time."""

    __tablename__ = "price_history"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="NGN")
    availability: Mapped[str] = mapped_column(String(50), nullable=True)
    source: Mapped[str] = mapped_column(String(100), default="scraper")

    # Relationships
    product = relationship("Product", back_populates="price_history")

    def __repr__(self) -> str:
        """String representation."""
        return f"<PriceHistory(id={self.id}, product_id={self.product_id}, price={self.price})>"
