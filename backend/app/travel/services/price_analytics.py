"""Travel price analytics service."""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.travel.models.flight import Flight
from app.travel.models.hotel import Hotel
from app.travel.models.price_history import TravelPriceHistory


class TravelPriceAnalytics:
    """Analytics service for travel price trends and statistics."""

    @staticmethod
    def get_flight_price_stats(db: Session, flight_id: int, days: int = 30) -> Optional[Dict]:
        """Get price statistics for a flight over specified period."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        prices = (
            db.query(TravelPriceHistory)
            .filter(
                TravelPriceHistory.flight_id == flight_id,
                TravelPriceHistory.created_at >= cutoff_date,
            )
            .order_by(TravelPriceHistory.created_at.desc())
            .all()
        )

        if not prices:
            return None

        price_values = [float(p.price) for p in prices]
        current_price = price_values[0]
        lowest_price = min(price_values)
        highest_price = max(price_values)
        average_price = sum(price_values) / len(price_values)

        price_drop = highest_price - current_price
        price_drop_percent = (price_drop / highest_price * 100) if highest_price > 0 else 0

        savings_from_avg = average_price - current_price
        savings_percent = (savings_from_avg / average_price * 100) if average_price > 0 else 0

        return {
            "flight_id": flight_id,
            "period_days": days,
            "current_price": current_price,
            "lowest_price": lowest_price,
            "highest_price": highest_price,
            "average_price": round(average_price, 2),
            "price_drop": round(price_drop, 2),
            "price_drop_percentage": round(price_drop_percent, 2),
            "savings_from_average": round(savings_from_avg, 2),
            "savings_percentage": round(savings_percent, 2),
            "data_points": len(prices),
        }

    @staticmethod
    def get_hotel_price_stats(db: Session, hotel_id: int, days: int = 30) -> Optional[Dict]:
        """Get price statistics for a hotel over specified period."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        prices = (
            db.query(TravelPriceHistory)
            .filter(
                TravelPriceHistory.hotel_id == hotel_id,
                TravelPriceHistory.created_at >= cutoff_date,
            )
            .order_by(TravelPriceHistory.created_at.desc())
            .all()
        )

        if not prices:
            return None

        price_values = [float(p.price) for p in prices]
        current_price = price_values[0]
        lowest_price = min(price_values)
        highest_price = max(price_values)
        average_price = sum(price_values) / len(price_values)

        price_drop = highest_price - current_price
        price_drop_percent = (price_drop / highest_price * 100) if highest_price > 0 else 0

        savings_from_avg = average_price - current_price
        savings_percent = (savings_from_avg / average_price * 100) if average_price > 0 else 0

        return {
            "hotel_id": hotel_id,
            "period_days": days,
            "current_price": current_price,
            "lowest_price": lowest_price,
            "highest_price": highest_price,
            "average_price": round(average_price, 2),
            "price_drop": round(price_drop, 2),
            "price_drop_percentage": round(price_drop_percent, 2),
            "savings_from_average": round(savings_from_avg, 2),
            "savings_percentage": round(savings_percent, 2),
            "data_points": len(prices),
        }

    @staticmethod
    def get_price_trend(db: Session, item_id: int, item_type: str, days: int = 7) -> str:
        """Determine price trend (rising, falling, stable)."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        if item_type == "flight":
            filter_condition = TravelPriceHistory.flight_id == item_id
        else:
            filter_condition = TravelPriceHistory.hotel_id == item_id

        prices = (
            db.query(TravelPriceHistory.price)
            .filter(
                filter_condition,
                TravelPriceHistory.created_at >= cutoff_date,
            )
            .order_by(TravelPriceHistory.created_at.asc())
            .all()
        )

        if len(prices) < 2:
            return "stable"

        first_price = float(prices[0][0])
        last_price = float(prices[-1][0])

        change_percent = ((last_price - first_price) / first_price * 100) if first_price > 0 else 0

        if change_percent > 5:
            return "rising"
        elif change_percent < -5:
            return "falling"
        else:
            return "stable"

    @staticmethod
    def get_multi_period_stats(db: Session, item_id: int, item_type: str) -> Dict:
        """Get statistics for multiple time periods."""
        periods = [7, 30, 60, 90]
        stats = {}

        for days in periods:
            if item_type == "flight":
                period_stats = TravelPriceAnalytics.get_flight_price_stats(db, item_id, days)
            else:
                period_stats = TravelPriceAnalytics.get_hotel_price_stats(db, item_id, days)
            
            if period_stats:
                stats[f"last_{days}_days"] = period_stats

        stats["trend_7_days"] = TravelPriceAnalytics.get_price_trend(db, item_id, item_type, 7)
        stats["trend_30_days"] = TravelPriceAnalytics.get_price_trend(db, item_id, item_type, 30)

        return stats

    @staticmethod
    def get_price_history_chart(
        db: Session, item_id: int, item_type: str, days: int = 30
    ) -> List[Dict]:
        """Get price history data formatted for charting."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        if item_type == "flight":
            filter_condition = TravelPriceHistory.flight_id == item_id
        else:
            filter_condition = TravelPriceHistory.hotel_id == item_id

        prices = (
            db.query(TravelPriceHistory)
            .filter(
                filter_condition,
                TravelPriceHistory.created_at >= cutoff_date,
            )
            .order_by(TravelPriceHistory.created_at.asc())
            .all()
        )

        return [
            {
                "date": p.created_at.isoformat(),
                "price": float(p.price),
            }
            for p in prices
        ]

    @staticmethod
    def get_price_volatility(db: Session, item_id: int, item_type: str, days: int = 30) -> Dict:
        """Calculate price volatility (coefficient of variation)."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        if item_type == "flight":
            filter_condition = TravelPriceHistory.flight_id == item_id
        else:
            filter_condition = TravelPriceHistory.hotel_id == item_id

        result = (
            db.query(
                func.avg(TravelPriceHistory.price).label("mean"),
                func.stddev(TravelPriceHistory.price).label("stddev"),
            )
            .filter(
                filter_condition,
                TravelPriceHistory.created_at >= cutoff_date,
            )
            .first()
        )

        if not result or not result.mean or not result.stddev:
            return {"volatility": 0, "interpretation": "insufficient_data"}

        mean = float(result.mean)
        stddev = float(result.stddev)
        cv = (stddev / mean * 100) if mean > 0 else 0

        if cv < 10:
            interpretation = "low"
        elif cv < 20:
            interpretation = "moderate"
        else:
            interpretation = "high"

        return {
            "volatility": round(cv, 2),
            "interpretation": interpretation,
            "mean_price": round(mean, 2),
            "std_deviation": round(stddev, 2),
        }

    @staticmethod
    def is_good_deal(db: Session, item_id: int, item_type: str, threshold: float = 10.0) -> bool:
        """Check if current price is a good deal compared to average."""
        if item_type == "flight":
            stats = TravelPriceAnalytics.get_flight_price_stats(db, item_id, 30)
        else:
            stats = TravelPriceAnalytics.get_hotel_price_stats(db, item_id, 30)

        if not stats:
            return False

        return stats["savings_percentage"] >= threshold

    @staticmethod
    def get_destination_price_trends(db: Session, destination: str, days: int = 30) -> Dict:
        """Get average price trends for a destination."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Flight prices to destination
        flights = db.query(Flight).filter(Flight.destination.ilike(f"%{destination}%")).all()
        flight_ids = [f.id for f in flights]

        flight_result = None
        if flight_ids:
            flight_result = (
                db.query(
                    func.avg(TravelPriceHistory.price).label("avg_price"),
                    func.min(TravelPriceHistory.price).label("min_price"),
                    func.max(TravelPriceHistory.price).label("max_price"),
                )
                .filter(
                    TravelPriceHistory.flight_id.in_(flight_ids),
                    TravelPriceHistory.created_at >= cutoff_date,
                )
                .first()
            )

        # Hotel prices in destination
        hotels = db.query(Hotel).filter(Hotel.location.ilike(f"%{destination}%")).all()
        hotel_ids = [h.id for h in hotels]

        hotel_result = None
        if hotel_ids:
            hotel_result = (
                db.query(
                    func.avg(TravelPriceHistory.price).label("avg_price"),
                    func.min(TravelPriceHistory.price).label("min_price"),
                    func.max(TravelPriceHistory.price).label("max_price"),
                )
                .filter(
                    TravelPriceHistory.hotel_id.in_(hotel_ids),
                    TravelPriceHistory.created_at >= cutoff_date,
                )
                .first()
            )

        return {
            "destination": destination,
            "flights": {
                "count": len(flights),
                "average_price": float(flight_result.avg_price) if flight_result and flight_result.avg_price else 0,
                "min_price": float(flight_result.min_price) if flight_result and flight_result.min_price else 0,
                "max_price": float(flight_result.max_price) if flight_result and flight_result.max_price else 0,
            },
            "hotels": {
                "count": len(hotels),
                "average_price": float(hotel_result.avg_price) if hotel_result and hotel_result.avg_price else 0,
                "min_price": float(hotel_result.min_price) if hotel_result and hotel_result.min_price else 0,
                "max_price": float(hotel_result.max_price) if hotel_result and hotel_result.max_price else 0,
            },
            "period_days": days,
        }