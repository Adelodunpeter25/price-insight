"""Product model for e-commerce tracking."""

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.base import BaseModel


class Product(BaseModel):
    """Product model for tracking e-commerce items."""
    
    __tablename__ = "products"
    
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False, unique=True, index=True)
    site: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    is_tracked: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    
    # Relationships
    price_history = relationship("PriceHistory", back_populates="product")
    deals = relationship("Deal", back_populates="product")
    alert_rules = relationship("AlertRule", back_populates="product")
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<Product(id={self.id}, name='{self.name[:50]}...', site='{self.site}')>"