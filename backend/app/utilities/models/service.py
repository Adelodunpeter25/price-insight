"""Utility service model for utilities and subscriptions."""

from sqlalchemy import Column, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.core.models.base import BaseModel


class UtilityService(BaseModel):
    """Utility service model for utilities and subscriptions."""

    __tablename__ = "utility_services"

    name = Column(String(200), nullable=False)
    service_type = Column(
        String(50), nullable=False, index=True
    )  # electricity, water, internet, streaming, software
    provider = Column(String(100), nullable=False, index=True)  # NEPA, MTN, Netflix, DSTV
    billing_type = Column(
        String(20), nullable=False, default="subscription"
    )  # prepaid, postpaid, subscription
    billing_cycle = Column(String(20), nullable=True)  # monthly, quarterly, yearly
    base_price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="NGN")
    plan_details = Column(Text, nullable=True)  # JSON string of plan features
    url = Column(Text, nullable=False)
    site = Column(String(100), nullable=False)
    is_tracked = Column(Integer, nullable=False, default=1)

    # Relationships
    price_history = relationship("UtilityPriceHistory", back_populates="service")

    def __repr__(self) -> str:
        """String representation."""
        return f"<UtilityService {self.name} - {self.provider} ₦{self.base_price}>"
