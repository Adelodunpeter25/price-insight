"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_database_session
from app.core.models.user import User
from app.core.schemas.auth import RefreshToken, Token, UserCreate, UserLogin, UserResponse
from app.core.security import verify_token
from app.core.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_database_session)):
    """Register new user."""
    auth_service = AuthService(db)
    user = await auth_service.register_user(
        email=user_data.email, password=user_data.password, full_name=user_data.full_name
    )
    return UserResponse.model_validate(user)


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_database_session)):
    """Login user."""
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(user_data.email, user_data.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    tokens = auth_service.create_user_tokens(user)
    return Token(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: RefreshToken, db: AsyncSession = Depends(get_database_session)):
    """Refresh access token."""
    payload = verify_token(token_data.refresh_token, "refresh")
    email = payload.get("sub")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    auth_service = AuthService(db)
    user = await auth_service.get_user_by_email(email)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    tokens = auth_service.create_user_tokens(user)
    return Token(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info."""
    return UserResponse.model_validate(current_user)
