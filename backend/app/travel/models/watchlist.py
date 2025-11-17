"""Travel watchlist model."""

from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, DECIMAL, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.base import BaseModel


class TravelWatchlist(BaseModel):
    """Travel watchlist model for tracking flights and hotels."""

    __tablename__ = "travel_watchlists"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    flight_id: Mapped[Optional[int]] = mapped_column(ForeignKey("flights.id"), nullable=True, index=True)
    hotel_id: Mapped[Optional[int]] = mapped_column(ForeignKey("hotels.id"), nullable=True, index=True)
    target_price: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2), nullable=True)
    alert_on_any_drop: Mapped[bool] = mapped_column(Boolean, default=True)
    alert_on_target: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user = relationship("User")
    flight = relationship("Flight", back_populates="watchlists")
    hotel = relationship("Hotel", back_populates="watchlists")

    def __repr__(self) -> str:
        """String representation."""
        item_type = "Flight" if self.flight_id else "Hotel"
        item_id = self.flight_id or self.hotel_id
        return f"<TravelWatchlist(user={self.user_id}, {item_type}={item_id})>"