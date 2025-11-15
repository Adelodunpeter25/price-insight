"""Property watchlist model."""

from decimal import Decimal

from sqlalchemy import DECIMAL, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.base import BaseModel


class PropertyWatchlist(BaseModel):
    """Property watchlist model for user tracking."""

    __tablename__ = "property_watchlists"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.id"), nullable=False, index=True
    )
    target_price: Mapped[Decimal] = mapped_column(DECIMAL(15, 2), nullable=True)
    alert_on_any_drop: Mapped[bool] = mapped_column(Boolean, default=True)
    alert_on_target: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str] = mapped_column(String(500), nullable=True)

    user = relationship("User")
    property = relationship("Property")

    def __repr__(self) -> str:
        """String representation."""
        return f"<PropertyWatchlist(user_id={self.user_id}, property_id={self.property_id})>"
