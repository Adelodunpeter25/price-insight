"""Deal model for tracking product deals and discounts."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DECIMAL, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.base import BaseModel


class Deal(BaseModel):
    """Deal model for tracking product deals and discounts."""

    __tablename__ = "deals"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    original_price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    deal_price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    discount_percent: Mapped[Decimal] = mapped_column(DECIMAL(5, 2), nullable=False)
    deal_type: Mapped[str] = mapped_column(
        String(50), default="price_drop"
    )  # price_drop, coupon, sale
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    deal_start_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    deal_end_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    product = relationship("Product", back_populates="deals")

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<Deal(id={self.id}, product_id={self.product_id}, discount={self.discount_percent}%)>"
        )

    @property
    def is_active(self) -> bool:
        """Check if deal is currently active."""
        now = datetime.utcnow()
        if self.deal_end_date and now > self.deal_end_date:
            return False
        if self.deal_start_date and now < self.deal_start_date:
            return False
        return self.is_active  # From BaseModel
