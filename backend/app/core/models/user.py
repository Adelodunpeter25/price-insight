"""User model."""

from sqlalchemy import Boolean, Column, String

from app.core.models.base import BaseModel


class User(BaseModel):
    """User model."""

    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False, index=True)

    def __repr__(self) -> str:
        """String representation."""
        return f"<User {self.email}>"
