"""Utility deal model."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text

from app.core.models.base import BaseModel


class UtilityDeal(BaseModel):
    """Utility deal model for promotions and rate changes."""

    __tablename__ = "utility_deals"

    service_id = Column(Integer, ForeignKey("utility_services.id"), nullable=False, index=True)
    deal_type = Column(String(50), nullable=False)  # promotion, rate_change, free_trial
    discount_percent = Column(Numeric(5, 2), nullable=True)
    original_price = Column(Numeric(10, 2), nullable=True)
    deal_price = Column(Numeric(10, 2), nullable=False)
    deal_start_date = Column(DateTime, nullable=True)
    deal_end_date = Column(DateTime, nullable=True)
    deal_source = Column(String(100), default="scraper")
    deal_description = Column(Text, nullable=True)

    def __repr__(self) -> str:
        """String representation."""
        return f"<UtilityDeal {self.deal_type} ₦{self.deal_price}>"
