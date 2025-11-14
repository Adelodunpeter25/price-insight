"""Deal preference model for user-specific deal alerts."""

from decimal import Decimal
from typing import List

from sqlalchemy import Column, Integer, ForeignKey, DECIMAL, Boolean, Text
from sqlalchemy.orm import relationship

from app.core.models.base import BaseModel


class DealPreference(BaseModel):
    """User preferences for deal alerts on tracked products."""
    
    __tablename__ = "deal_preferences"
    
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Deal alert settings
    enable_deal_alerts = Column(Boolean, default=True, nullable=False)
    min_discount_percent = Column(DECIMAL(5, 2), default=10.0, nullable=False)
    max_price_threshold = Column(DECIMAL(10, 2), nullable=True)
    
    # Deal types (stored as JSON string)
    deal_types = Column(Text, default='["percentage"]', nullable=False)  # JSON array
    
    # Relationships
    product = relationship("Product", backref="deal_preferences")
    user = relationship("User", backref="deal_preferences")
    
    def get_deal_types(self) -> List[str]:
        """Get deal types as list."""
        import json
        try:
            return json.loads(self.deal_types)
        except:
            return ["percentage"]
    
    def set_deal_types(self, types: List[str]) -> None:
        """Set deal types from list."""
        import json
        self.deal_types = json.dumps(types)