"""Travel price history model for tracking price changes."""

from decimal import Decimal

from sqlalchemy import DECIMAL, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.base import BaseModel


class TravelPriceHistory(BaseModel):
    """Travel price history model for tracking price changes over time."""

    __tablename__ = "travel_price_history"

    flight_id: Mapped[int] = mapped_column(ForeignKey("flights.id"), nullable=True, index=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"), nullable=True, index=True)
    price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="NGN")
    source: Mapped[str] = mapped_column(String(100), default="scraper")

    # Relationships
    flight = relationship("Flight", backref="price_history")
    hotel = relationship("Hotel", backref="price_history")

    def __repr__(self) -> str:
        """String representation."""
        item_id = self.flight_id or self.hotel_id
        item_type = "flight" if self.flight_id else "hotel"
        return f"<TravelPriceHistory(id={self.id}, {item_type}_id={item_id}, price={self.price})>"
