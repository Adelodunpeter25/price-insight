"""Utility alert models."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text

from app.core.models.base import BaseModel


class UtilityAlertRule(BaseModel):
    """Utility alert rule model."""

    __tablename__ = "utility_alert_rules"

    service_id = Column(Integer, ForeignKey("utility_services.id"), nullable=True, index=True)
    service_type = Column(String(50), nullable=True, index=True)
    provider = Column(String(100), nullable=True, index=True)
    max_price = Column(Numeric(10, 2), nullable=True)
    rule_type = Column(String(50), nullable=False)  # price_increase, promotion, rate_change
    threshold_value = Column(Numeric(10, 2), nullable=True)
    percentage_threshold = Column(Numeric(5, 2), nullable=True)
    notification_method = Column(String(50), default="console")

    def __repr__(self) -> str:
        """String representation."""
        return f"<UtilityAlertRule {self.rule_type}>"


class UtilityAlertHistory(BaseModel):
    """Utility alert history model."""

    __tablename__ = "utility_alert_history"

    rule_id = Column(Integer, ForeignKey("utility_alert_rules.id"), nullable=False, index=True)
    service_id = Column(Integer, ForeignKey("utility_services.id"), nullable=True, index=True)
    alert_type = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    triggered_at = Column(DateTime, nullable=False)
    notification_sent = Column(Integer, default=0)

    def __repr__(self) -> str:
        """String representation."""
        return f"<UtilityAlertHistory {self.alert_type}>"
