"""Travel deal models."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text

from app.core.models.base import BaseModel


class TravelDeal(BaseModel):
    """Travel deal model."""

    __tablename__ = "travel_deals"

    flight_id = Column(Integer, ForeignKey("flights.id"), nullable=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=True)
    discount_percent = Column(Numeric(5, 2), nullable=True)
    original_price = Column(Numeric(10, 2), nullable=True)
    deal_price = Column(Numeric(10, 2), nullable=False)
    deal_start_date = Column(DateTime, nullable=True)
    deal_end_date = Column(DateTime, nullable=True)
    deal_source = Column(String(100), nullable=False)
    deal_description = Column(Text, nullable=True)

    def __repr__(self) -> str:
        """String representation."""
        item_id = self.flight_id or self.hotel_id
        item_type = "flight" if self.flight_id else "hotel"
        return f"<TravelDeal {item_type}:{item_id} {self.discount_percent}%>"