"""Travel deal preference model."""

from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, DECIMAL, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.base import BaseModel


class TravelDealPreference(BaseModel):
    """Travel deal preference model for user-specific deal criteria."""

    __tablename__ = "travel_deal_preferences"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    flight_id: Mapped[Optional[int]] = mapped_column(ForeignKey("flights.id"), nullable=True, index=True)
    hotel_id: Mapped[Optional[int]] = mapped_column(ForeignKey("hotels.id"), nullable=True, index=True)
    min_discount_percent: Mapped[Decimal] = mapped_column(DECIMAL(5, 2), default=15.0)
    max_price_threshold: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2), nullable=True)
    deal_types: Mapped[str] = mapped_column(String(255), default='["percentage", "fixed"]')  # JSON array
    enable_deal_alerts: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    user = relationship("User")
    flight = relationship("Flight", back_populates="deal_preferences")
    hotel = relationship("Hotel", back_populates="deal_preferences")

    def get_deal_types(self) -> list:
        """Parse deal types from JSON string."""
        import json
        try:
            return json.loads(self.deal_types)
        except (json.JSONDecodeError, TypeError):
            return ["percentage", "fixed"]

    def __repr__(self) -> str:
        """String representation."""
        item_type = "Flight" if self.flight_id else "Hotel"
        return f"<TravelDealPreference(user={self.user_id}, {item_type}, min_discount={self.min_discount_percent}%)>"