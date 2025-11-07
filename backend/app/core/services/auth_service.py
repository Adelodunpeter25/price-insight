"""Authentication service."""

import logging
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import log_event
from app.core.models.user import User
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.core.services.email_service import EmailService

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service."""

    def __init__(self, db: AsyncSession):
        """Initialize service."""
        self.db = db
        self.email_service = EmailService()

    async def register_user(
        self, email: str, password: str, full_name: Optional[str] = None
    ) -> User:
        """Register new user."""
        # Check if user exists
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
            )

        # Create user
        hashed_pwd = hash_password(password)
        user = User(email=email, hashed_password=hashed_pwd, full_name=full_name)

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        # Send welcome email
        try:
            await self.email_service.send_welcome_email(
                to_email=user.email, user_name=user.full_name or user.email.split("@")[0]
            )
            log_event("user_welcome_email_sent", {"user_id": user.id, "email": user.email})
        except Exception as e:
            logger.error(f"Failed to send welcome email to {user.email}: {e}")

        return user

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user credentials."""
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.hashed_password):
            return None

        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    def create_user_tokens(self, user: User) -> dict:
        """Create access and refresh tokens for user."""
        token_data = {"sub": user.email, "user_id": user.id}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        return {"access_token": access_token, "refresh_token": refresh_token}
