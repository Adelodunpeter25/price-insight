"""Deal preferences API endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.models.user import User
from app.ecommerce.models import Product, DealPreference
from app.ecommerce.schemas import (
    DealPreferenceCreate,
    DealPreferenceResponse,
    DealPreferenceUpdate,
)

router = APIRouter(prefix="/api/e-commerce/deal-preferences", tags=["Deal Preferences"])


@router.post("/", response_model=DealPreferenceResponse, status_code=201)
async def create_deal_preference(
    preference_data: DealPreferenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create deal preference for a product."""
    # Check if product exists
    product = db.query(Product).filter(
        Product.id == preference_data.product_id,
        Product.is_active == True
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if preference already exists
    existing = db.query(DealPreference).filter(
        DealPreference.product_id == preference_data.product_id,
        DealPreference.user_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Deal preference already exists for this product")
    
    # Create preference
    preference = DealPreference(
        product_id=preference_data.product_id,
        user_id=current_user.id,
        enable_deal_alerts=preference_data.enable_deal_alerts,
        min_discount_percent=preference_data.min_discount_percent,
        max_price_threshold=preference_data.max_price_threshold,
    )
    preference.set_deal_types(preference_data.deal_types)
    
    db.add(preference)
    db.commit()
    db.refresh(preference)
    
    return DealPreferenceResponse.model_validate(preference)


@router.get("/", response_model=List[DealPreferenceResponse])
async def list_deal_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List user's deal preferences."""
    preferences = db.query(DealPreference).filter(
        DealPreference.user_id == current_user.id
    ).all()
    
    return [DealPreferenceResponse.model_validate(pref) for pref in preferences]


@router.get("/{preference_id}", response_model=DealPreferenceResponse)
async def get_deal_preference(
    preference_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get specific deal preference."""
    preference = db.query(DealPreference).filter(
        DealPreference.id == preference_id,
        DealPreference.user_id == current_user.id
    ).first()
    
    if not preference:
        raise HTTPException(status_code=404, detail="Deal preference not found")
    
    return DealPreferenceResponse.model_validate(preference)


@router.patch("/{preference_id}", response_model=DealPreferenceResponse)
async def update_deal_preference(
    preference_id: int,
    preference_data: DealPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update deal preference."""
    preference = db.query(DealPreference).filter(
        DealPreference.id == preference_id,
        DealPreference.user_id == current_user.id
    ).first()
    
    if not preference:
        raise HTTPException(status_code=404, detail="Deal preference not found")
    
    # Update fields
    update_data = preference_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "deal_types":
            preference.set_deal_types(value)
        else:
            setattr(preference, field, value)
    
    db.commit()
    db.refresh(preference)
    
    return DealPreferenceResponse.model_validate(preference)


@router.delete("/{preference_id}", status_code=204)
async def delete_deal_preference(
    preference_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete deal preference."""
    preference = db.query(DealPreference).filter(
        DealPreference.id == preference_id,
        DealPreference.user_id == current_user.id
    ).first()
    
    if not preference:
        raise HTTPException(status_code=404, detail="Deal preference not found")
    
    db.delete(preference)
    db.commit()
    
    return None