"""Flight model for travel price tracking."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Column, Date, DateTime, Integer, Numeric, String, Text

from app.core.models.base import BaseModel


class Flight(BaseModel):
    """Flight price tracking model."""

    __tablename__ = "flights"

    origin = Column(String(10), nullable=False, index=True)
    destination = Column(String(10), nullable=False, index=True)
    departure_date = Column(Date, nullable=False, index=True)
    return_date = Column(Date, nullable=True)
    airline = Column(String(100), nullable=True)
    flight_class = Column(String(20), nullable=False, default="economy")
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    url = Column(Text, nullable=False)
    site = Column(String(100), nullable=False)
    passengers = Column(Integer, nullable=False, default=1)
    is_tracked = Column(Integer, nullable=False, default=1)

    def __repr__(self) -> str:
        """String representation."""
        return f"<Flight {self.origin}-{self.destination} ${self.price}>"