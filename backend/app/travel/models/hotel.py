"""Hotel model for travel price tracking."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.travel.models.deal import TravelDeal
    from app.travel.models.deal_preference import TravelDealPreference
    from app.travel.models.price_history import TravelPriceHistory
    from app.travel.models.watchlist import TravelWatchlist

from sqlalchemy import Column, Date, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

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
    currency = Column(String(3), nullable=False, default="NGN")
    url = Column(Text, nullable=False)
    site = Column(String(100), nullable=False)
    guests = Column(Integer, nullable=False, default=2)
    rating = Column(Numeric(2, 1), nullable=True)
    is_tracked = Column(Integer, nullable=False, default=1)

    # Relationships
    price_history = relationship("TravelPriceHistory", back_populates="hotel")
    deals = relationship("TravelDeal", back_populates="hotel")
    watchlists = relationship("TravelWatchlist", back_populates="hotel")
    deal_preferences = relationship("TravelDealPreference", back_populates="hotel")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Hotel {self.name} ${self.total_price}>"
