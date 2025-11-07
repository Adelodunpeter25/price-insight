"""Real estate deal model."""

from decimal import Decimal

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text

from app.core.models.base import BaseModel


class PropertyDeal(BaseModel):
    """Property deal model for price drops and special offers."""

    __tablename__ = "property_deals"

    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False, index=True)
    deal_type = Column(String(50), nullable=False)  # price_drop, new_listing, expired
    discount_percent = Column(Numeric(5, 2), nullable=True)
    original_price = Column(Numeric(15, 2), nullable=True)
    deal_price = Column(Numeric(15, 2), nullable=False)
    deal_start_date = Column(DateTime, nullable=True)
    deal_end_date = Column(DateTime, nullable=True)
    deal_source = Column(String(100), default="scraper")
    deal_description = Column(Text, nullable=True)

    def __repr__(self) -> str:
        """String representation."""
        return f"<PropertyDeal {self.deal_type} ₦{self.deal_price}>"