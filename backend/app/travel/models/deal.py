"""Travel deal model for tracking flight and hotel deals."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DECIMAL, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.base import BaseModel


class TravelDeal(BaseModel):
    """Travel deal model for tracking flight and hotel deals and discounts."""

    __tablename__ = "travel_deals"

    flight_id: Mapped[Optional[int]] = mapped_column(ForeignKey("flights.id"), nullable=True, index=True)
    hotel_id: Mapped[Optional[int]] = mapped_column(ForeignKey("hotels.id"), nullable=True, index=True)
    original_price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    deal_price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    discount_percent: Mapped[Decimal] = mapped_column(DECIMAL(5, 2), nullable=False)
    deal_type: Mapped[str] = mapped_column(String(50), default="price_drop")  # price_drop, sale, last_minute
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    deal_start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deal_end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    flight = relationship("Flight", back_populates="deals")
    hotel = relationship("Hotel", back_populates="deals")

    def __repr__(self) -> str:
        """String representation."""
        item_type = "Flight" if self.flight_id else "Hotel"
        item_id = self.flight_id or self.hotel_id
        return f"<TravelDeal({item_type}={item_id}, discount={self.discount_percent}%)>"

    @property
    def is_deal_active(self) -> bool:
        """Check if deal is currently active."""
        now = datetime.utcnow()
        if self.deal_end_date and now > self.deal_end_date:
            return False
        if self.deal_start_date and now < self.deal_start_date:
            return False
        return self.is_active  # From BaseModel

    @property
    def savings(self) -> Decimal:
        """Calculate savings amount."""
        return self.original_price - self.deal_price