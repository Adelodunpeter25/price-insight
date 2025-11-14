"""In-app notifications API endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.models.user import User
from app.core.services.notification_service import NotificationService, Notification

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("/", response_model=List[dict])
async def get_notifications(
    unread_only: bool = False,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user notifications."""
    service = NotificationService(db)
    notifications = service.get_user_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit
    )
    
    return [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "type": n.type,
            "is_read": n.is_read,
            "created_at": n.created_at,
            "data": n.data
        }
        for n in notifications
    ]


@router.get("/unread-count")
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get count of unread notifications."""
    service = NotificationService(db)
    count = service.get_unread_count(current_user.id)
    return {"unread_count": count}


@router.patch("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark notification as read."""
    service = NotificationService(db)
    success = service.mark_as_read(notification_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification marked as read"}


@router.patch("/mark-all-read")
async def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark all notifications as read."""
    service = NotificationService(db)
    count = service.mark_all_as_read(current_user.id)
    return {"message": f"Marked {count} notifications as read"}