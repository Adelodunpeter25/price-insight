"""In-app notification service."""

import logging
from datetime import datetime
from typing import List, Optional
from enum import Enum

from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.models.base import BaseModel
from app.core.models.user import User

logger = logging.getLogger(__name__)


class NotificationType(str, Enum):
    """Notification types."""
    PRICE_DROP = "price_drop"
    DEAL_ALERT = "deal_alert"
    SYSTEM = "system"
    WELCOME = "welcome"


class Notification(BaseModel):
    """In-app notification model."""
    
    __tablename__ = "notifications"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), nullable=False, default=NotificationType.SYSTEM)
    is_read = Column(Boolean, default=False, nullable=False)
    data = Column(Text, nullable=True)  # JSON data for additional context
    
    # Relationships
    user = relationship("User", backref="notifications")


class NotificationService:
    """Service for managing in-app notifications."""
    
    def __init__(self, db: Session):
        """Initialize notification service."""
        self.db = db
    
    def create_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.SYSTEM,
        data: Optional[str] = None
    ) -> Notification:
        """Create new in-app notification."""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type,
            data=data
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        logger.info(f"Created notification for user {user_id}: {title}")
        return notification
    
    def get_user_notifications(
        self, 
        user_id: int, 
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Notification]:
        """Get notifications for user."""
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
            
        return query.order_by(Notification.created_at.desc()).limit(limit).all()
    
    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """Mark notification as read."""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification:
            notification.is_read = True
            self.db.commit()
            return True
        return False
    
    def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications as read for user."""
        count = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True})
        
        self.db.commit()
        return count
    
    def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications."""
        return self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()
    
    def notify_price_drop(self, user_id: int, product_name: str, old_price: float, new_price: float) -> Notification:
        """Create price drop notification."""
        savings = old_price - new_price
        discount = ((old_price - new_price) / old_price) * 100
        
        return self.create_notification(
            user_id=user_id,
            title=f"Price Drop: {product_name}",
            message=f"Price dropped by {discount:.1f}% - Save ₦{savings:,.2f}",
            notification_type=NotificationType.PRICE_DROP,
            data=f'{{"product_name": "{product_name}", "old_price": {old_price}, "new_price": {new_price}}}'
        )
    
    def notify_deal_alert(self, user_id: int, product_name: str, discount_percent: float) -> Notification:
        """Create deal alert notification."""
        return self.create_notification(
            user_id=user_id,
            title=f"🔥 Hot Deal: {product_name}",
            message=f"Amazing {discount_percent:.1f}% discount available now!",
            notification_type=NotificationType.DEAL_ALERT,
            data=f'{{"product_name": "{product_name}", "discount": {discount_percent}}}'
        )