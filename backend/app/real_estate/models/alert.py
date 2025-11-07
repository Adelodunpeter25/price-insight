"""Property alert models."""

from decimal import Decimal

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text

from app.core.models.base import BaseModel


class PropertyAlertRule(BaseModel):
    """Property alert rule model."""

    __tablename__ = "property_alert_rules"

    property_id = Column(Integer, ForeignKey("properties.id"), nullable=True, index=True)
    location = Column(String(200), nullable=True, index=True)
    property_type = Column(String(50), nullable=True)
    max_price = Column(Numeric(15, 2), nullable=True)
    min_bedrooms = Column(Integer, nullable=True)
    rule_type = Column(String(50), nullable=False)  # price_drop, new_listing, location_alert
    threshold_value = Column(Numeric(15, 2), nullable=True)
    percentage_threshold = Column(Numeric(5, 2), nullable=True)
    notification_method = Column(String(50), default="console")

    def __repr__(self) -> str:
        """String representation."""
        return f"<PropertyAlertRule {self.rule_type}>"


class PropertyAlertHistory(BaseModel):
    """Property alert history model."""

    __tablename__ = "property_alert_history"

    rule_id = Column(Integer, ForeignKey("property_alert_rules.id"), nullable=False, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=True, index=True)
    alert_type = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    triggered_at = Column(DateTime, nullable=False)
    notification_sent = Column(Integer, default=0)

    def __repr__(self) -> str:
        """String representation."""
        return f"<PropertyAlertHistory {self.alert_type}>"