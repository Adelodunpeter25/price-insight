"""Travel alert models."""

from sqlalchemy import Column, ForeignKey, Integer, Numeric, String

from app.core.models.base import BaseModel


class TravelAlertRule(BaseModel):
    """Travel-specific alert rules."""

    __tablename__ = "travel_alert_rules"

    flight_id = Column(Integer, ForeignKey("flights.id"), nullable=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=True)
    rule_type = Column(String(50), nullable=False)  # price_drop, threshold, deal
    threshold_value = Column(Numeric(10, 2), nullable=True)
    percentage_threshold = Column(Numeric(5, 2), nullable=True)
    notification_method = Column(String(50), nullable=False, default="console")

    def __repr__(self) -> str:
        """String representation."""
        item_id = self.flight_id or self.hotel_id
        item_type = "flight" if self.flight_id else "hotel"
        return f"<TravelAlertRule {item_type}:{item_id} {self.rule_type}>"


class TravelAlertHistory(BaseModel):
    """Travel alert history."""

    __tablename__ = "travel_alert_history"

    alert_rule_id = Column(Integer, ForeignKey("travel_alert_rules.id"), nullable=False)
    flight_id = Column(Integer, ForeignKey("flights.id"), nullable=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=True)
    trigger_value = Column(Numeric(10, 2), nullable=False)
    message = Column(String(500), nullable=False)
    notification_sent = Column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:
        """String representation."""
        return f"<TravelAlertHistory {self.message[:50]}>"