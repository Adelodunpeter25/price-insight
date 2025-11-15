"""Property deal preference model."""

from decimal import Decimal

from sqlalchemy import DECIMAL, Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.base import BaseModel


class PropertyDealPreference(BaseModel):
    """User preferences for property deal alerts."""

    __tablename__ = "property_deal_preferences"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.id"), nullable=True, index=True
    )
    location: Mapped[str] = mapped_column(String(200), nullable=True)
    property_type: Mapped[str] = mapped_column(String(50), nullable=True)
    min_discount_percent: Mapped[Decimal] = mapped_column(DECIMAL(5, 2), nullable=True)
    max_price_threshold: Mapped[Decimal] = mapped_column(DECIMAL(15, 2), nullable=True)
    min_bedrooms: Mapped[int] = mapped_column(Integer, nullable=True)
    enable_deal_alerts: Mapped[bool] = mapped_column(Boolean, default=True)

    user = relationship("User")
    property = relationship("Property")

    def __repr__(self) -> str:
        """String representation."""
        return f"<PropertyDealPreference(user_id={self.user_id}, location={self.location})>"
