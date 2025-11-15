"""Property price analytics service."""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.real_estate.models.price_history import PropertyPriceHistory
from app.real_estate.models.property import Property


class PropertyPriceAnalytics:
    """Analytics service for property price trends and statistics."""

    @staticmethod
    def get_price_stats(db: Session, property_id: int, days: int = 30) -> Optional[Dict]:
        """Get price statistics for a property over specified period."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        prices = (
            db.query(PropertyPriceHistory)
            .filter(
                PropertyPriceHistory.property_id == property_id,
                PropertyPriceHistory.created_at >= cutoff_date,
            )
            .order_by(PropertyPriceHistory.created_at.desc())
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
            "property_id": property_id,
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
    def get_price_trend(db: Session, property_id: int, days: int = 7) -> str:
        """Determine price trend (rising, falling, stable)."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        prices = (
            db.query(PropertyPriceHistory.price)
            .filter(
                PropertyPriceHistory.property_id == property_id,
                PropertyPriceHistory.created_at >= cutoff_date,
            )
            .order_by(PropertyPriceHistory.created_at.asc())
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
    def get_multi_period_stats(db: Session, property_id: int) -> Dict:
        """Get statistics for multiple time periods."""
        periods = [7, 30, 60, 90]
        stats = {}

        for days in periods:
            period_stats = PropertyPriceAnalytics.get_price_stats(db, property_id, days)
            if period_stats:
                stats[f"last_{days}_days"] = period_stats

        stats["trend_7_days"] = PropertyPriceAnalytics.get_price_trend(db, property_id, 7)
        stats["trend_30_days"] = PropertyPriceAnalytics.get_price_trend(db, property_id, 30)

        return stats

    @staticmethod
    def get_price_history_chart(
        db: Session, property_id: int, days: int = 30
    ) -> List[Dict]:
        """Get price history data formatted for charting."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        prices = (
            db.query(PropertyPriceHistory)
            .filter(
                PropertyPriceHistory.property_id == property_id,
                PropertyPriceHistory.created_at >= cutoff_date,
            )
            .order_by(PropertyPriceHistory.created_at.asc())
            .all()
        )

        return [
            {
                "date": p.created_at.isoformat(),
                "price": float(p.price),
                "price_per_sqm": float(p.price_per_sqm) if p.price_per_sqm else None,
            }
            for p in prices
        ]

    @staticmethod
    def get_price_volatility(db: Session, property_id: int, days: int = 30) -> Dict:
        """Calculate price volatility (coefficient of variation)."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        result = (
            db.query(
                func.avg(PropertyPriceHistory.price).label("mean"),
                func.stddev(PropertyPriceHistory.price).label("stddev"),
            )
            .filter(
                PropertyPriceHistory.property_id == property_id,
                PropertyPriceHistory.created_at >= cutoff_date,
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
    def is_good_deal(db: Session, property_id: int, threshold: float = 10.0) -> bool:
        """Check if current price is a good deal compared to average."""
        stats = PropertyPriceAnalytics.get_price_stats(db, property_id, 30)

        if not stats:
            return False

        return stats["savings_percentage"] >= threshold

    @staticmethod
    def get_location_price_trends(db: Session, location: str, days: int = 30) -> Dict:
        """Get average price trends for a location."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        properties = db.query(Property).filter(Property.location.ilike(f"%{location}%")).all()

        if not properties:
            return {"location": location, "properties_count": 0}

        property_ids = [p.id for p in properties]

        result = (
            db.query(
                func.avg(PropertyPriceHistory.price).label("avg_price"),
                func.min(PropertyPriceHistory.price).label("min_price"),
                func.max(PropertyPriceHistory.price).label("max_price"),
            )
            .filter(
                PropertyPriceHistory.property_id.in_(property_ids),
                PropertyPriceHistory.created_at >= cutoff_date,
            )
            .first()
        )

        return {
            "location": location,
            "properties_count": len(properties),
            "average_price": float(result.avg_price) if result.avg_price else 0,
            "min_price": float(result.min_price) if result.min_price else 0,
            "max_price": float(result.max_price) if result.max_price else 0,
            "period_days": days,
        }
