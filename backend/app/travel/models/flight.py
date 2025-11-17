"""Flight model for travel price tracking."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.travel.models.deal import TravelDeal
    from app.travel.models.deal_preference import TravelDealPreference
    from app.travel.models.price_history import TravelPriceHistory
    from app.travel.models.watchlist import TravelWatchlist

from sqlalchemy import Column, Date, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

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
    currency = Column(String(3), nullable=False, default="NGN")
    url = Column(Text, nullable=False)
    site = Column(String(100), nullable=False)
    passengers = Column(Integer, nullable=False, default=1)
    is_tracked = Column(Integer, nullable=False, default=1)

    # Relationships
    price_history = relationship("TravelPriceHistory", back_populates="flight")
    deals = relationship("TravelDeal", back_populates="flight")
    watchlists = relationship("TravelWatchlist", back_populates="flight")
    deal_preferences = relationship("TravelDealPreference", back_populates="flight")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Flight {self.origin}-{self.destination} ${self.price}>"
