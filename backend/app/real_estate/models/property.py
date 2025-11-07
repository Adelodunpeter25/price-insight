"""Property model for real estate listings."""

from sqlalchemy import Column, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.core.models.base import BaseModel


class Property(BaseModel):
    """Real estate property model."""

    __tablename__ = "properties"

    name = Column(String(200), nullable=False)
    property_type = Column(String(50), nullable=False, index=True)  # house, apartment, land
    location = Column(String(200), nullable=False, index=True)
    bedrooms = Column(Integer, nullable=True)
    bathrooms = Column(Integer, nullable=True)
    size_sqm = Column(Numeric(10, 2), nullable=True)
    price = Column(Numeric(15, 2), nullable=False, index=True)
    price_per_sqm = Column(Numeric(10, 2), nullable=True)
    listing_type = Column(String(20), nullable=False, default="sale")  # sale, rent
    currency = Column(String(3), nullable=False, default="NGN")
    agent = Column(String(200), nullable=True)
    url = Column(Text, nullable=False)
    site = Column(String(100), nullable=False)
    features = Column(Text, nullable=True)  # JSON string of features
    is_tracked = Column(Integer, nullable=False, default=1)

    # Relationships
    price_history = relationship("PropertyPriceHistory", back_populates="property")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Property {self.name} ₦{self.price}>"
