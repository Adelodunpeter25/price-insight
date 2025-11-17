"""Travel deal detection service."""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Union

from sqlalchemy.orm import Session

from app.core.deal_detection.base_detector import BaseDealDetector
from app.travel.models.deal import TravelDeal
from app.travel.models.flight import Flight
from app.travel.models.hotel import Hotel
from app.travel.models.price_history import TravelPriceHistory
from app.travel.services.price_analytics import TravelPriceAnalytics

logger = logging.getLogger(__name__)


class TravelDealDetector(BaseDealDetector):
    """Deal detector for travel items (flights and hotels)."""

    def get_items_for_detection(self, db: Session) -> List[Union[Flight, Hotel]]:
        """Get active flights and hotels for deal detection."""
        flights = db.query(Flight).filter(Flight.is_active, Flight.price.isnot(None)).all()
        hotels = db.query(Hotel).filter(Hotel.is_active, Hotel.total_price.isnot(None)).all()
        return flights + hotels

    def get_price_history(self, db: Session, item: Union[Flight, Hotel]) -> List[TravelPriceHistory]:
        """Get price history for flight or hotel."""
        if isinstance(item, Flight):
            return (
                db.query(TravelPriceHistory)
                .filter(TravelPriceHistory.flight_id == item.id)
                .order_by(TravelPriceHistory.created_at.desc())
                .limit(30)
                .all()
            )
        else:  # Hotel
            return (
                db.query(TravelPriceHistory)
                .filter(TravelPriceHistory.hotel_id == item.id)
                .order_by(TravelPriceHistory.created_at.desc())
                .limit(30)
                .all()
            )

    def get_current_price(self, item: Union[Flight, Hotel]) -> Optional[Decimal]:
        """Get current price from flight or hotel."""
        if isinstance(item, Flight):
            return item.price
        else:  # Hotel
            return item.total_price

    def create_deal(self, db: Session, item: Union[Flight, Hotel], deal_data: Dict) -> Optional[TravelDeal]:
        """Create travel deal record with analytics."""
        try:
            item_type = "flight" if isinstance(item, Flight) else "hotel"
            
            if item_type == "flight":
                stats = TravelPriceAnalytics.get_flight_price_stats(db, item.id, 30)
            else:
                stats = TravelPriceAnalytics.get_hotel_price_stats(db, item.id, 30)
            
            trend = TravelPriceAnalytics.get_price_trend(db, item.id, item_type, 7)

            if isinstance(item, Flight):
                description = f"{item.origin}-{item.destination} flight: {deal_data['discount_percent']:.1f}% off - Save ₦{deal_data['savings']:.2f}"
            else:
                description = f"{item.name} hotel: {deal_data['discount_percent']:.1f}% off - Save ₦{deal_data['savings']:.2f}"

            if stats and stats['current_price'] == stats['lowest_price']:
                description += " | Lowest price in 30 days!"
            elif trend == "falling":
                description += " | Price trending down"

            # Check for existing deal
            if isinstance(item, Flight):
                existing_deal = (
                    db.query(TravelDeal)
                    .filter(TravelDeal.flight_id == item.id, TravelDeal.is_active == True)
                    .first()
                )
            else:
                existing_deal = (
                    db.query(TravelDeal)
                    .filter(TravelDeal.hotel_id == item.id, TravelDeal.is_active == True)
                    .first()
                )

            if existing_deal:
                existing_deal.discount_percent = deal_data["discount_percent"]
                existing_deal.original_price = deal_data["original_price"]
                existing_deal.deal_price = deal_data["current_price"]
                existing_deal.description = description
                existing_deal.updated_at = datetime.utcnow()
                return existing_deal
            else:
                deal = TravelDeal(
                    flight_id=item.id if isinstance(item, Flight) else None,
                    hotel_id=item.id if isinstance(item, Hotel) else None,
                    deal_type="price_drop",
                    description=description,
                    original_price=deal_data["original_price"],
                    deal_price=deal_data["current_price"],
                    discount_percent=deal_data["discount_percent"],
                )
                db.add(deal)
                db.flush()
                return deal

        except Exception as e:
            logger.error(f"Failed to create travel deal: {e}")
            return None