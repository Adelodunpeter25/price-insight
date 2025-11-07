"""Property price history model."""

from decimal import Decimal

from sqlalchemy import DECIMAL, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.base import BaseModel


class PropertyPriceHistory(BaseModel):
    """Property price history model."""

    __tablename__ = "property_price_history"

    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.id"), nullable=False, index=True
    )
    price: Mapped[Decimal] = mapped_column(DECIMAL(15, 2), nullable=False)
    price_per_sqm: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="NGN")
    listing_status: Mapped[str] = mapped_column(String(50), nullable=True)
    source: Mapped[str] = mapped_column(String(100), default="scraper")

    # Relationships
    property = relationship("Property", back_populates="price_history")

    def __repr__(self) -> str:
        """String representation."""
        return f"<PropertyPriceHistory(property_id={self.property_id}, price=₦{self.price})>"
