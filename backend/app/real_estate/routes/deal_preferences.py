"""Property deal preference API endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.models.user import User
from app.real_estate.models.deal_preference import PropertyDealPreference

router = APIRouter(
    prefix="/api/real-estate/deal-preferences", tags=["Real Estate Deal Preferences"]
)


class DealPreferenceCreate(BaseModel):
    """Schema for creating deal preference."""

    property_id: int = None
    location: str = None
    property_type: str = None
    min_discount_percent: float = None
    max_price_threshold: float = None
    min_bedrooms: int = None
    enable_deal_alerts: bool = True


class DealPreferenceResponse(BaseModel):
    """Schema for deal preference response."""

    id: int
    user_id: int
    property_id: int = None
    location: str = None
    property_type: str = None
    min_discount_percent: float = None
    max_price_threshold: float = None
    min_bedrooms: int = None
    enable_deal_alerts: bool

    class Config:
        from_attributes = True


@router.post("/", response_model=DealPreferenceResponse, status_code=201)
def create_deal_preference(
    data: DealPreferenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create deal preference."""
    preference = PropertyDealPreference(
        user_id=current_user.id,
        property_id=data.property_id,
        location=data.location,
        property_type=data.property_type,
        min_discount_percent=data.min_discount_percent,
        max_price_threshold=data.max_price_threshold,
        min_bedrooms=data.min_bedrooms,
        enable_deal_alerts=data.enable_deal_alerts,
    )

    db.add(preference)
    db.commit()
    db.refresh(preference)

    return preference


@router.get("/", response_model=List[DealPreferenceResponse])
def get_deal_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's deal preferences."""
    preferences = (
        db.query(PropertyDealPreference)
        .filter(
            PropertyDealPreference.user_id == current_user.id,
            PropertyDealPreference.is_active == True,
        )
        .all()
    )

    return preferences


@router.patch("/{preference_id}", response_model=DealPreferenceResponse)
def update_deal_preference(
    preference_id: int,
    data: DealPreferenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update deal preference."""
    preference = (
        db.query(PropertyDealPreference)
        .filter(
            PropertyDealPreference.id == preference_id,
            PropertyDealPreference.user_id == current_user.id,
            PropertyDealPreference.is_active == True,
        )
        .first()
    )

    if not preference:
        raise HTTPException(status_code=404, detail="Preference not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(preference, key, value)

    db.commit()
    db.refresh(preference)

    return preference


@router.delete("/{preference_id}", status_code=204)
def delete_deal_preference(
    preference_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete deal preference."""
    preference = (
        db.query(PropertyDealPreference)
        .filter(
            PropertyDealPreference.id == preference_id,
            PropertyDealPreference.user_id == current_user.id,
            PropertyDealPreference.is_active == True,
        )
        .first()
    )

    if not preference:
        raise HTTPException(status_code=404, detail="Preference not found")

    preference.is_active = False
    db.commit()

    return None
