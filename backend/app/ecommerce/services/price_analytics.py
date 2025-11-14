"""Price analytics service for trend analysis and statistics."""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.ecommerce.models.price_history import PriceHistory

logger = logging.getLogger(__name__)


class PriceAnalytics:
    """Service for analyzing price trends and statistics."""

    @staticmethod
    def get_price_stats(db: Session, product_id: int, days: int = 30) -> Optional[Dict]:
        """Get price statistics for a product over specified days."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            prices = db.query(PriceHistory).filter(
                PriceHistory.product_id == product_id,
                PriceHistory.created_at >= cutoff_date
            ).order_by(PriceHistory.created_at.asc()).all()
            
            if not prices:
                return None
            
            price_values = [float(p.price) for p in prices]
            current_price = price_values[-1]
            lowest_price = min(price_values)
            highest_price = max(price_values)
            avg_price = sum(price_values) / len(price_values)
            
            # Calculate price drop percentage from highest
            price_drop_pct = ((highest_price - current_price) / highest_price * 100) if highest_price > 0 else 0
            
            # Calculate savings from average
            savings_from_avg = avg_price - current_price
            savings_pct = (savings_from_avg / avg_price * 100) if avg_price > 0 else 0
            
            return {
                "current_price": current_price,
                "lowest_price": lowest_price,
                "highest_price": highest_price,
                "average_price": round(avg_price, 2),
                "price_drop_percentage": round(price_drop_pct, 2),
                "savings_from_average": round(savings_from_avg, 2),
                "savings_percentage": round(savings_pct, 2),
                "data_points": len(prices),
                "period_days": days,
                "first_tracked": prices[0].created_at.isoformat(),
                "last_updated": prices[-1].created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating price stats for product {product_id}: {e}")
            return None

    @staticmethod
    def get_price_trend(db: Session, product_id: int, days: int = 7) -> str:
        """Calculate price trend (rising/falling/stable)."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            prices = db.query(PriceHistory).filter(
                PriceHistory.product_id == product_id,
                PriceHistory.created_at >= cutoff_date
            ).order_by(PriceHistory.created_at.asc()).all()
            
            if len(prices) < 2:
                return "insufficient_data"
            
            price_values = [float(p.price) for p in prices]
            first_price = price_values[0]
            last_price = price_values[-1]
            
            change_pct = ((last_price - first_price) / first_price * 100) if first_price > 0 else 0
            
            if change_pct > 5:
                return "rising"
            elif change_pct < -5:
                return "falling"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"Error calculating price trend for product {product_id}: {e}")
            return "error"

    @staticmethod
    def get_price_history_chart(db: Session, product_id: int, days: int = 30) -> List[Dict]:
        """Get price history data for charting."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            prices = db.query(PriceHistory).filter(
                PriceHistory.product_id == product_id,
                PriceHistory.created_at >= cutoff_date
            ).order_by(PriceHistory.created_at.asc()).all()
            
            return [
                {
                    "date": p.created_at.isoformat(),
                    "price": float(p.price),
                    "availability": p.availability
                }
                for p in prices
            ]
            
        except Exception as e:
            logger.error(f"Error getting price history for product {product_id}: {e}")
            return []

    @staticmethod
    def get_multi_period_stats(db: Session, product_id: int) -> Dict:
        """Get price statistics for multiple time periods."""
        try:
            return {
                "last_7_days": PriceAnalytics.get_price_stats(db, product_id, 7),
                "last_30_days": PriceAnalytics.get_price_stats(db, product_id, 30),
                "last_60_days": PriceAnalytics.get_price_stats(db, product_id, 60),
                "last_90_days": PriceAnalytics.get_price_stats(db, product_id, 90),
                "trend_7_days": PriceAnalytics.get_price_trend(db, product_id, 7),
                "trend_30_days": PriceAnalytics.get_price_trend(db, product_id, 30)
            }
            
        except Exception as e:
            logger.error(f"Error getting multi-period stats for product {product_id}: {e}")
            return {}

    @staticmethod
    def is_good_deal(db: Session, product_id: int, threshold_pct: float = 10.0) -> bool:
        """Check if current price is a good deal based on historical data."""
        try:
            stats = PriceAnalytics.get_price_stats(db, product_id, 30)
            if not stats:
                return False
            
            current = stats["current_price"]
            average = stats["average_price"]
            
            discount_pct = ((average - current) / average * 100) if average > 0 else 0
            
            return discount_pct >= threshold_pct
            
        except Exception as e:
            logger.error(f"Error checking deal status for product {product_id}: {e}")
            return False

    @staticmethod
    def get_price_volatility(db: Session, product_id: int, days: int = 30) -> Optional[float]:
        """Calculate price volatility (standard deviation)."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            prices = db.query(PriceHistory).filter(
                PriceHistory.product_id == product_id,
                PriceHistory.created_at >= cutoff_date
            ).all()
            
            if len(prices) < 2:
                return None
            
            price_values = [float(p.price) for p in prices]
            avg = sum(price_values) / len(price_values)
            variance = sum((x - avg) ** 2 for x in price_values) / len(price_values)
            std_dev = variance ** 0.5
            
            # Return coefficient of variation (CV) as percentage
            cv = (std_dev / avg * 100) if avg > 0 else 0
            return round(cv, 2)
            
        except Exception as e:
            logger.error(f"Error calculating volatility for product {product_id}: {e}")
            return None
