"""Travel deal detection service."""

import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from app.core.deal_detection.base_detector import BaseDealDetector
from app.travel.models.deal import TravelDeal
from app.travel.models.flight import Flight
from app.travel.models.hotel import Hotel
from app.travel.models.price_history import TravelPriceHistory


class TravelDealDetector(BaseDealDetector):
    """Deal detector for travel services."""

    def get_items_for_detection(self, db: Session) -> List[Any]:
        """Get active travel items for deal detection."""
        flights = db.query(Flight).filter(Flight.is_tracked == 1, Flight.price.isnot(None)).all()

        hotels = (
            db.query(Hotel).filter(Hotel.is_tracked == 1, Hotel.price_per_night.isnot(None)).all()
        )

        return flights + hotels

    def get_price_history(self, db: Session, item: Any) -> List[TravelPriceHistory]:
        """Get price history for travel item."""
        if isinstance(item, Flight):
            return (
                db.query(TravelPriceHistory)
                .filter(TravelPriceHistory.flight_id == item.id)
                .order_by(TravelPriceHistory.recorded_at.desc())
                .limit(30)
                .all()
            )
        elif isinstance(item, Hotel):
            return (
                db.query(TravelPriceHistory)
                .filter(TravelPriceHistory.hotel_id == item.id)
                .order_by(TravelPriceHistory.recorded_at.desc())
                .limit(30)
                .all()
            )
        return []

    def get_current_price(self, item: Any) -> Optional[Decimal]:
        """Get current price from travel item."""
        if isinstance(item, Flight):
            return item.price
        elif isinstance(item, Hotel):
            return item.price_per_night
        return None

    def create_deal(self, db: Session, item: Any, deal_data: Dict) -> Optional[TravelDeal]:
        """Create travel deal record using existing service."""
        try:
            # Determine parameters for deal service
            if isinstance(item, Flight):
                flight_id = item.id
                hotel_id = None
            elif isinstance(item, Hotel):
                flight_id = None
                hotel_id = item.id
            else:
                return None

            # Check if deal already exists
            existing_deal = (
                db.query(TravelDeal)
                .filter(
                    (
                        TravelDeal.flight_id == flight_id
                        if flight_id
                        else TravelDeal.hotel_id == hotel_id
                    ),
                    TravelDeal.is_active,
                )
                .first()
            )

            if existing_deal:
                # Update existing deal
                existing_deal.discount_percent = float(deal_data["discount_percent"])
                existing_deal.original_price = float(deal_data["original_price"])
                existing_deal.deal_price = float(deal_data["current_price"])
                existing_deal.deal_description = (
                    f"{deal_data['discount_percent']:.1f}% off - Save ₦{deal_data['savings']:.2f}"
                )
                return existing_deal
            else:
                # Create new deal
                deal = TravelDeal(
                    flight_id=flight_id,
                    hotel_id=hotel_id,
                    discount_percent=float(deal_data["discount_percent"]),
                    original_price=float(deal_data["original_price"]),
                    deal_price=float(deal_data["current_price"]),
                    deal_description=f"{deal_data['discount_percent']:.1f}% off - Save ₦{deal_data['savings']:.2f}",
                    deal_source="automated",
                    is_active=True,
                )
                db.add(deal)
                db.flush()
                return deal

        except Exception as e:
            logger.error(f"Failed to create travel deal: {e}")
            return None
