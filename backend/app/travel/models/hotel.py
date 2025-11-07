"""Hotel model for travel price tracking."""

from datetime import date
from decimal import Decimal

from sqlalchemy import Column, Date, Integer, Numeric, String, Text

from app.core.models.base import BaseModel


class Hotel(BaseModel):
    """Hotel price tracking model."""

    __tablename__ = "hotels"

    name = Column(String(200), nullable=False)
    location = Column(String(200), nullable=False, index=True)
    check_in = Column(Date, nullable=False, index=True)
    check_out = Column(Date, nullable=False, index=True)
    room_type = Column(String(100), nullable=False)
    price_per_night = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    url = Column(Text, nullable=False)
    site = Column(String(100), nullable=False)
    guests = Column(Integer, nullable=False, default=2)
    rating = Column(Numeric(2, 1), nullable=True)
    is_tracked = Column(Integer, nullable=False, default=1)

    def __repr__(self) -> str:
        """String representation."""
        return f"<Hotel {self.name} ${self.total_price}>"