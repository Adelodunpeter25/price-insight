"""Watchlist model for tracking user product interests."""

from decimal import Decimal

from sqlalchemy import DECIMAL, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.base import BaseModel


class Watchlist(BaseModel):
    """Watchlist model for user product tracking."""

    __tablename__ = "watchlists"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    target_price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=True)
    alert_on_any_drop: Mapped[bool] = mapped_column(Boolean, default=True)
    alert_on_target: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str] = mapped_column(String(500), nullable=True)

    # Relationships
    user = relationship("User", back_populates="watchlists")
    product = relationship("Product", back_populates="watchlists")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Watchlist(user_id={self.user_id}, product_id={self.product_id})>"
