"""Travel analytics dashboard service."""

from datetime import datetime, timedelta
from typing import Dict, List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.travel.models.deal import TravelDeal
from app.travel.models.flight import Flight
from app.travel.models.hotel import Hotel
from app.travel.models.price_history import TravelPriceHistory
from app.travel.models.watchlist import TravelWatchlist


class TravelAnalyticsDashboard:
    """Analytics dashboard for travel insights."""

    @staticmethod
    def get_user_dashboard(db: Session, user_id: int, days: int = 30) -> Dict:
        """Get user-specific dashboard metrics."""
        watchlist_count = (
            db.query(func.count(TravelWatchlist.id))
            .filter(TravelWatchlist.user_id == user_id, TravelWatchlist.is_active == True)
            .scalar()
        )

        # Get user's watchlist items
        watchlist_flights = (
            db.query(TravelWatchlist.flight_id)
            .filter(
                TravelWatchlist.user_id == user_id,
                TravelWatchlist.flight_id.isnot(None),
                TravelWatchlist.is_active == True
            )
            .all()
        )
        flight_ids = [f[0] for f in watchlist_flights]

        watchlist_hotels = (
            db.query(TravelWatchlist.hotel_id)
            .filter(
                TravelWatchlist.user_id == user_id,
                TravelWatchlist.hotel_id.isnot(None),
                TravelWatchlist.is_active == True
            )
            .all()
        )
        hotel_ids = [h[0] for h in watchlist_hotels]

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Count deals on watchlist items
        flight_deals = 0
        hotel_deals = 0
        
        if flight_ids:
            flight_deals = (
                db.query(func.count(TravelDeal.id))
                .filter(
                    TravelDeal.flight_id.in_(flight_ids),
                    TravelDeal.created_at >= cutoff_date,
                    TravelDeal.is_active == True,
                )
                .scalar() or 0
            )

        if hotel_ids:
            hotel_deals = (
                db.query(func.count(TravelDeal.id))
                .filter(
                    TravelDeal.hotel_id.in_(hotel_ids),
                    TravelDeal.created_at >= cutoff_date,
                    TravelDeal.is_active == True,
                )
                .scalar() or 0
            )

        # Calculate potential savings
        flight_savings = 0
        hotel_savings = 0

        if flight_ids:
            flight_savings = (
                db.query(func.sum(TravelDeal.original_price - TravelDeal.deal_price))
                .filter(
                    TravelDeal.flight_id.in_(flight_ids),
                    TravelDeal.created_at >= cutoff_date,
                    TravelDeal.is_active == True,
                )
                .scalar() or 0
            )

        if hotel_ids:
            hotel_savings = (
                db.query(func.sum(TravelDeal.original_price - TravelDeal.deal_price))
                .filter(
                    TravelDeal.hotel_id.in_(hotel_ids),
                    TravelDeal.created_at >= cutoff_date,
                    TravelDeal.is_active == True,
                )
                .scalar() or 0
            )

        return {
            "watchlist_count": watchlist_count or 0,
            "flight_deals": flight_deals,
            "hotel_deals": hotel_deals,
            "total_deals": flight_deals + hotel_deals,
            "flight_savings": float(flight_savings),
            "hotel_savings": float(hotel_savings),
            "total_savings": float(flight_savings + hotel_savings),
            "period_days": days,
        }

    @staticmethod
    def get_global_dashboard(db: Session, days: int = 30) -> Dict:
        """Get platform-wide dashboard metrics."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        total_flights = (
            db.query(func.count(Flight.id)).filter(Flight.is_active == True).scalar()
        )

        total_hotels = (
            db.query(func.count(Hotel.id)).filter(Hotel.is_active == True).scalar()
        )

        total_deals = (
            db.query(func.count(TravelDeal.id))
            .filter(TravelDeal.created_at >= cutoff_date, TravelDeal.is_active == True)
            .scalar()
        )

        total_savings = (
            db.query(func.sum(TravelDeal.original_price - TravelDeal.deal_price))
            .filter(TravelDeal.created_at >= cutoff_date, TravelDeal.is_active == True)
            .scalar()
        )

        total_tracking = (
            db.query(func.count(TravelWatchlist.id))
            .filter(TravelWatchlist.is_active == True)
            .scalar()
        )

        return {
            "total_flights_tracked": total_flights or 0,
            "total_hotels_tracked": total_hotels or 0,
            "total_travel_items": (total_flights or 0) + (total_hotels or 0),
            "total_active_deals": total_deals or 0,
            "total_savings": float(total_savings or 0),
            "total_users_tracking": total_tracking or 0,
            "period_days": days,
        }

    @staticmethod
    def get_total_savings(db: Session, user_id: int, days: int = 30) -> Dict:
        """Get total savings statistics."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get user's watchlist items
        watchlist_flights = (
            db.query(TravelWatchlist.flight_id)
            .filter(
                TravelWatchlist.user_id == user_id,
                TravelWatchlist.flight_id.isnot(None),
                TravelWatchlist.is_active == True
            )
            .all()
        )
        flight_ids = [f[0] for f in watchlist_flights]

        watchlist_hotels = (
            db.query(TravelWatchlist.hotel_id)
            .filter(
                TravelWatchlist.user_id == user_id,
                TravelWatchlist.hotel_id.isnot(None),
                TravelWatchlist.is_active == True
            )
            .all()
        )
        hotel_ids = [h[0] for h in watchlist_hotels]

        all_item_ids = []
        if flight_ids:
            all_item_ids.extend([("flight", fid) for fid in flight_ids])
        if hotel_ids:
            all_item_ids.extend([("hotel", hid) for hid in hotel_ids])

        if not all_item_ids:
            return {
                "total_deals": 0,
                "total_savings": 0,
                "average_discount": 0,
                "flight_deals": 0,
                "hotel_deals": 0,
                "period_days": days,
            }

        # Get flight deals
        flight_result = None
        if flight_ids:
            flight_result = (
                db.query(
                    func.count(TravelDeal.id).label("deal_count"),
                    func.sum(TravelDeal.original_price - TravelDeal.deal_price).label("total_savings"),
                    func.avg(TravelDeal.discount_percent).label("avg_discount"),
                )
                .filter(
                    TravelDeal.flight_id.in_(flight_ids),
                    TravelDeal.created_at >= cutoff_date,
                    TravelDeal.is_active == True,
                )
                .first()
            )

        # Get hotel deals
        hotel_result = None
        if hotel_ids:
            hotel_result = (
                db.query(
                    func.count(TravelDeal.id).label("deal_count"),
                    func.sum(TravelDeal.original_price - TravelDeal.deal_price).label("total_savings"),
                    func.avg(TravelDeal.discount_percent).label("avg_discount"),
                )
                .filter(
                    TravelDeal.hotel_id.in_(hotel_ids),
                    TravelDeal.created_at >= cutoff_date,
                    TravelDeal.is_active == True,
                )
                .first()
            )

        flight_deals = flight_result.deal_count if flight_result else 0
        hotel_deals = hotel_result.deal_count if hotel_result else 0
        
        flight_savings = float(flight_result.total_savings or 0) if flight_result else 0
        hotel_savings = float(hotel_result.total_savings or 0) if hotel_result else 0
        
        flight_discount = float(flight_result.avg_discount or 0) if flight_result else 0
        hotel_discount = float(hotel_result.avg_discount or 0) if hotel_result else 0

        total_deals = flight_deals + hotel_deals
        total_savings = flight_savings + hotel_savings
        avg_discount = ((flight_discount + hotel_discount) / 2) if (flight_discount or hotel_discount) else 0

        return {
            "total_deals": total_deals,
            "total_savings": total_savings,
            "average_discount": round(avg_discount, 2),
            "flight_deals": flight_deals,
            "hotel_deals": hotel_deals,
            "flight_savings": flight_savings,
            "hotel_savings": hotel_savings,
            "period_days": days,
        }

    @staticmethod
    def get_most_searched_destinations(db: Session, limit: int = 10) -> List[Dict]:
        """Get most searched destinations."""
        # Flight destinations
        flight_destinations = (
            db.query(
                Flight.destination.label("destination"),
                func.count(TravelWatchlist.id).label("search_count"),
            )
            .join(TravelWatchlist, Flight.id == TravelWatchlist.flight_id)
            .filter(TravelWatchlist.is_active == True, Flight.is_active == True)
            .group_by(Flight.destination)
            .order_by(func.count(TravelWatchlist.id).desc())
            .limit(limit)
            .all()
        )

        # Hotel locations
        hotel_locations = (
            db.query(
                Hotel.location.label("destination"),
                func.count(TravelWatchlist.id).label("search_count"),
            )
            .join(TravelWatchlist, Hotel.id == TravelWatchlist.hotel_id)
            .filter(TravelWatchlist.is_active == True, Hotel.is_active == True)
            .group_by(Hotel.location)
            .order_by(func.count(TravelWatchlist.id).desc())
            .limit(limit)
            .all()
        )

        # Combine and sort
        all_destinations = {}
        
        for dest, count in flight_destinations:
            all_destinations[dest] = all_destinations.get(dest, 0) + count
            
        for dest, count in hotel_locations:
            all_destinations[dest] = all_destinations.get(dest, 0) + count

        sorted_destinations = sorted(all_destinations.items(), key=lambda x: x[1], reverse=True)

        return [
            {
                "destination": dest,
                "search_count": count,
            }
            for dest, count in sorted_destinations[:limit]
        ]

    @staticmethod
    def get_best_travel_deals(db: Session, days: int = 30, limit: int = 10) -> List[Dict]:
        """Get best travel deals by discount percentage."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        results = (
            db.query(TravelDeal, Flight, Hotel)
            .outerjoin(Flight, TravelDeal.flight_id == Flight.id)
            .outerjoin(Hotel, TravelDeal.hotel_id == Hotel.id)
            .filter(TravelDeal.created_at >= cutoff_date, TravelDeal.is_active == True)
            .order_by(TravelDeal.discount_percent.desc())
            .limit(limit)
            .all()
        )

        deals = []
        for deal, flight, hotel in results:
            if flight:
                deals.append({
                    "type": "flight",
                    "name": f"{flight.origin}-{flight.destination}",
                    "original_price": float(deal.original_price),
                    "deal_price": float(deal.deal_price),
                    "discount_percent": float(deal.discount_percent),
                    "savings": float(deal.savings),
                    "description": deal.description,
                })
            elif hotel:
                deals.append({
                    "type": "hotel",
                    "name": hotel.name,
                    "location": hotel.location,
                    "original_price": float(deal.original_price),
                    "deal_price": float(deal.deal_price),
                    "discount_percent": float(deal.discount_percent),
                    "savings": float(deal.savings),
                    "description": deal.description,
                })

        return deals

    @staticmethod
    def get_price_drop_statistics(db: Session, days: int = 30) -> Dict:
        """Get price drop statistics."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        total_flights = (
            db.query(func.count(Flight.id)).filter(Flight.is_active == True).scalar()
        )

        total_hotels = (
            db.query(func.count(Hotel.id)).filter(Hotel.is_active == True).scalar()
        )

        flights_with_drops = (
            db.query(func.count(func.distinct(TravelDeal.flight_id)))
            .filter(
                TravelDeal.flight_id.isnot(None),
                TravelDeal.created_at >= cutoff_date,
                TravelDeal.is_active == True
            )
            .scalar()
        )

        hotels_with_drops = (
            db.query(func.count(func.distinct(TravelDeal.hotel_id)))
            .filter(
                TravelDeal.hotel_id.isnot(None),
                TravelDeal.created_at >= cutoff_date,
                TravelDeal.is_active == True
            )
            .scalar()
        )

        total_items = total_flights + total_hotels
        items_with_drops = flights_with_drops + hotels_with_drops
        drop_rate = (items_with_drops / total_items * 100) if total_items > 0 else 0

        avg_drop = (
            db.query(func.avg(TravelDeal.original_price - TravelDeal.deal_price))
            .filter(TravelDeal.created_at >= cutoff_date, TravelDeal.is_active == True)
            .scalar()
        )

        avg_drop_percent = (
            db.query(func.avg(TravelDeal.discount_percent))
            .filter(TravelDeal.created_at >= cutoff_date, TravelDeal.is_active == True)
            .scalar()
        )

        biggest_drop = (
            db.query(
                TravelDeal,
                Flight.origin,
                Flight.destination,
                Hotel.name,
                (TravelDeal.original_price - TravelDeal.deal_price).label("drop_amount"),
            )
            .outerjoin(Flight, TravelDeal.flight_id == Flight.id)
            .outerjoin(Hotel, TravelDeal.hotel_id == Hotel.id)
            .filter(TravelDeal.created_at >= cutoff_date, TravelDeal.is_active == True)
            .order_by((TravelDeal.original_price - TravelDeal.deal_price).desc())
            .first()
        )

        return {
            "total_flights": total_flights or 0,
            "total_hotels": total_hotels or 0,
            "total_items": total_items,
            "flights_with_drops": flights_with_drops or 0,
            "hotels_with_drops": hotels_with_drops or 0,
            "items_with_drops": items_with_drops,
            "drop_rate_percentage": round(drop_rate, 2),
            "average_drop_amount": float(avg_drop or 0),
            "average_drop_percentage": float(avg_drop_percent or 0),
            "biggest_drop": (
                {
                    "type": "flight" if biggest_drop[1] else "hotel",
                    "name": f"{biggest_drop[1]}-{biggest_drop[2]}" if biggest_drop[1] else biggest_drop[3],
                    "drop_amount": float(biggest_drop[4]),
                    "drop_percentage": float(biggest_drop[0].discount_percent),
                }
                if biggest_drop
                else None
            ),
            "period_days": days,
        }