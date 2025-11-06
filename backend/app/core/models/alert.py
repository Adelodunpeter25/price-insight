"""Alert models for notification rules and history."""

from decimal import Decimal
from typing import Optional

from sqlalchemy import DECIMAL, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.base import BaseModel


class AlertRule(BaseModel):
    """Alert rule model for defining notification triggers."""

    __tablename__ = "alert_rules"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    rule_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # price_drop, threshold, deal_appeared
    threshold_value: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2), nullable=True)
    percentage_threshold: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(5, 2), nullable=True)
    notification_method: Mapped[str] = mapped_column(
        String(50), default="console"
    )  # console, email, file

    # Relationships
    product = relationship("Product", back_populates="alert_rules")
    alert_history = relationship("AlertHistory", back_populates="alert_rule")

    def __repr__(self) -> str:
        """String representation."""
        return f"<AlertRule(id={self.id}, type={self.rule_type}, product_id={self.product_id})>"


class AlertHistory(BaseModel):
    """Alert history model for tracking fired alerts."""

    __tablename__ = "alert_history"

    alert_rule_id: Mapped[int] = mapped_column(
        ForeignKey("alert_rules.id"), nullable=False, index=True
    )
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    trigger_value: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    notification_sent: Mapped[bool] = mapped_column(default=False)

    # Relationships
    alert_rule = relationship("AlertRule", back_populates="alert_history")
    product = relationship("Product")

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<AlertHistory(id={self.id}, rule_id={self.alert_rule_id}, "
            f"sent={self.notification_sent})>"
        )
