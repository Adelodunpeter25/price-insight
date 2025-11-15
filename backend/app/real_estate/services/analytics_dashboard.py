"""Property analytics dashboard service."""

from datetime import datetime, timedelta
from typing import Dict, List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.real_estate.models.deal import PropertyDeal
from app.real_estate.models.price_history import PropertyPriceHistory
from app.real_estate.models.property import Property
from app.real_estate.models.watchlist import PropertyWatchlist


class PropertyAnalyticsDashboard:
    """Analytics dashboard for property insights."""

    @staticmethod
    def get_user_dashboard(db: Session, user_id: int, days: int = 30) -> Dict:
        """Get user-specific dashboard metrics."""
        watchlist_count = (
            db.query(func.count(PropertyWatchlist.id))
            .filter(PropertyWatchlist.user_id == user_id, PropertyWatchlist.is_active == True)
            .scalar()
        )

        watchlist_properties = (
            db.query(PropertyWatchlist.property_id)
            .filter(PropertyWatchlist.user_id == user_id, PropertyWatchlist.is_active == True)
            .all()
        )
        property_ids = [p[0] for p in watchlist_properties]

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        deals_on_watchlist = (
            db.query(func.count(PropertyDeal.id))
            .filter(
                PropertyDeal.property_id.in_(property_ids),
                PropertyDeal.created_at >= cutoff_date,
                PropertyDeal.is_active == True,
            )
            .scalar()
            if property_ids
            else 0
        )

        potential_savings = (
            db.query(func.sum(PropertyDeal.original_price - PropertyDeal.deal_price))
            .filter(
                PropertyDeal.property_id.in_(property_ids),
                PropertyDeal.created_at >= cutoff_date,
                PropertyDeal.is_active == True,
            )
            .scalar()
            if property_ids
            else 0
        )

        return {
            "watchlist_count": watchlist_count or 0,
            "deals_on_watchlist": deals_on_watchlist or 0,
            "potential_savings": float(potential_savings or 0),
            "period_days": days,
        }

    @staticmethod
    def get_global_dashboard(db: Session, days: int = 30) -> Dict:
        """Get platform-wide dashboard metrics."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        total_properties = (
            db.query(func.count(Property.id)).filter(Property.is_active == True).scalar()
        )

        total_deals = (
            db.query(func.count(PropertyDeal.id))
            .filter(PropertyDeal.created_at >= cutoff_date, PropertyDeal.is_active == True)
            .scalar()
        )

        total_savings = (
            db.query(func.sum(PropertyDeal.original_price - PropertyDeal.deal_price))
            .filter(PropertyDeal.created_at >= cutoff_date, PropertyDeal.is_active == True)
            .scalar()
        )

        total_tracking = (
            db.query(func.count(PropertyWatchlist.id))
            .filter(PropertyWatchlist.is_active == True)
            .scalar()
        )

        return {
            "total_properties_tracked": total_properties or 0,
            "total_active_deals": total_deals or 0,
            "total_savings": float(total_savings or 0),
            "total_users_tracking": total_tracking or 0,
            "period_days": days,
        }

    @staticmethod
    def get_total_savings(db: Session, user_id: int, days: int = 30) -> Dict:
        """Get total savings statistics."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        watchlist_properties = (
            db.query(PropertyWatchlist.property_id)
            .filter(PropertyWatchlist.user_id == user_id, PropertyWatchlist.is_active == True)
            .all()
        )
        property_ids = [p[0] for p in watchlist_properties]

        if not property_ids:
            return {
                "total_deals": 0,
                "total_savings": 0,
                "average_discount": 0,
                "period_days": days,
            }

        result = (
            db.query(
                func.count(PropertyDeal.id).label("deal_count"),
                func.sum(PropertyDeal.original_price - PropertyDeal.deal_price).label(
                    "total_savings"
                ),
                func.avg(PropertyDeal.discount_percent).label("avg_discount"),
            )
            .filter(
                PropertyDeal.property_id.in_(property_ids),
                PropertyDeal.created_at >= cutoff_date,
                PropertyDeal.is_active == True,
            )
            .first()
        )

        return {
            "total_deals": result.deal_count or 0,
            "total_savings": float(result.total_savings or 0),
            "average_discount": float(result.avg_discount or 0),
            "period_days": days,
        }

    @staticmethod
    def get_most_tracked_properties(db: Session, limit: int = 10) -> List[Dict]:
        """Get most tracked properties."""
        results = (
            db.query(
                Property,
                func.count(PropertyWatchlist.id).label("watchlist_count"),
            )
            .join(PropertyWatchlist, Property.id == PropertyWatchlist.property_id)
            .filter(PropertyWatchlist.is_active == True, Property.is_active == True)
            .group_by(Property.id)
            .order_by(func.count(PropertyWatchlist.id).desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "property_id": prop.id,
                "name": prop.name,
                "location": prop.location,
                "price": float(prop.price),
                "property_type": prop.property_type,
                "watchlist_count": count,
            }
            for prop, count in results
        ]

    @staticmethod
    def get_best_value_areas(db: Session, days: int = 30, limit: int = 10) -> List[Dict]:
        """Get locations with best price drops."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        results = (
            db.query(
                Property.location,
                func.count(PropertyDeal.id).label("deal_count"),
                func.sum(PropertyDeal.original_price - PropertyDeal.deal_price).label(
                    "total_savings"
                ),
                func.avg(PropertyDeal.discount_percent).label("avg_discount"),
            )
            .join(PropertyDeal, Property.id == PropertyDeal.property_id)
            .filter(PropertyDeal.created_at >= cutoff_date, PropertyDeal.is_active == True)
            .group_by(Property.location)
            .order_by(func.count(PropertyDeal.id).desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "location": location,
                "deal_count": deal_count,
                "total_savings": float(total_savings or 0),
                "average_discount": float(avg_discount or 0),
            }
            for location, deal_count, total_savings, avg_discount in results
        ]

    @staticmethod
    def get_price_drop_statistics(db: Session, days: int = 30) -> Dict:
        """Get price drop statistics."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        total_properties = (
            db.query(func.count(Property.id)).filter(Property.is_active == True).scalar()
        )

        properties_with_drops = (
            db.query(func.count(func.distinct(PropertyDeal.property_id)))
            .filter(PropertyDeal.created_at >= cutoff_date, PropertyDeal.is_active == True)
            .scalar()
        )

        drop_rate = (
            (properties_with_drops / total_properties * 100) if total_properties > 0 else 0
        )

        avg_drop = (
            db.query(func.avg(PropertyDeal.original_price - PropertyDeal.deal_price))
            .filter(PropertyDeal.created_at >= cutoff_date, PropertyDeal.is_active == True)
            .scalar()
        )

        avg_drop_percent = (
            db.query(func.avg(PropertyDeal.discount_percent))
            .filter(PropertyDeal.created_at >= cutoff_date, PropertyDeal.is_active == True)
            .scalar()
        )

        biggest_drop = (
            db.query(
                Property.name,
                (PropertyDeal.original_price - PropertyDeal.deal_price).label("drop_amount"),
                PropertyDeal.discount_percent,
            )
            .join(PropertyDeal, Property.id == PropertyDeal.property_id)
            .filter(PropertyDeal.created_at >= cutoff_date, PropertyDeal.is_active == True)
            .order_by((PropertyDeal.original_price - PropertyDeal.deal_price).desc())
            .first()
        )

        return {
            "total_properties": total_properties or 0,
            "properties_with_drops": properties_with_drops or 0,
            "drop_rate_percentage": round(drop_rate, 2),
            "average_drop_amount": float(avg_drop or 0),
            "average_drop_percentage": float(avg_drop_percent or 0),
            "biggest_drop": (
                {
                    "property_name": biggest_drop[0],
                    "drop_amount": float(biggest_drop[1]),
                    "drop_percentage": float(biggest_drop[2]),
                }
                if biggest_drop
                else None
            ),
            "period_days": days,
        }
