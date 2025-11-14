"""Analytics dashboard service for e-commerce insights."""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from app.ecommerce.models.deal import Deal
from app.ecommerce.models.price_history import PriceHistory
from app.ecommerce.models.product import Product
from app.ecommerce.models.watchlist import Watchlist

logger = logging.getLogger(__name__)


class AnalyticsDashboard:
    """Service for generating analytics dashboard data."""

    @staticmethod
    def get_total_savings(db: Session, user_id: int = None, days: int = 30) -> Dict:
        """Calculate total savings from deals."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            query = db.query(
                func.count(Deal.id).label('total_deals'),
                func.sum(Deal.savings).label('total_savings'),
                func.avg(Deal.discount_percent).label('avg_discount')
            ).filter(
                Deal.is_active == True,
                Deal.created_at >= cutoff_date
            )
            
            if user_id:
                # Filter by user's watchlist products
                query = query.join(Watchlist, Deal.product_id == Watchlist.product_id).filter(
                    Watchlist.user_id == user_id
                )
            
            result = query.first()
            
            return {
                "total_deals": result.total_deals or 0,
                "total_savings": float(result.total_savings or 0),
                "average_discount": float(result.avg_discount or 0),
                "period_days": days
            }
            
        except Exception as e:
            logger.error(f"Error calculating total savings: {e}")
            return {"total_deals": 0, "total_savings": 0, "average_discount": 0, "period_days": days}

    @staticmethod
    def get_most_tracked_products(db: Session, limit: int = 10) -> List[Dict]:
        """Get most tracked products by watchlist count."""
        try:
            results = db.query(
                Product.id,
                Product.name,
                Product.site,
                Product.url,
                func.count(Watchlist.id).label('watchlist_count')
            ).join(
                Watchlist, Product.id == Watchlist.product_id
            ).group_by(
                Product.id
            ).order_by(
                desc('watchlist_count')
            ).limit(limit).all()
            
            products = []
            for r in results:
                # Get current price
                latest_price = db.query(PriceHistory).filter(
                    PriceHistory.product_id == r.id
                ).order_by(PriceHistory.created_at.desc()).first()
                
                products.append({
                    "product_id": r.id,
                    "name": r.name,
                    "site": r.site,
                    "url": r.url,
                    "watchlist_count": r.watchlist_count,
                    "current_price": float(latest_price.price) if latest_price else None
                })
            
            return products
            
        except Exception as e:
            logger.error(f"Error getting most tracked products: {e}")
            return []

    @staticmethod
    def get_best_retailers(db: Session, days: int = 30, limit: int = 10) -> List[Dict]:
        """Get best performing retailers by deal count and savings."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            results = db.query(
                Product.site,
                func.count(Deal.id).label('deal_count'),
                func.sum(Deal.savings).label('total_savings'),
                func.avg(Deal.discount_percent).label('avg_discount')
            ).join(
                Product, Deal.product_id == Product.id
            ).filter(
                Deal.is_active == True,
                Deal.created_at >= cutoff_date
            ).group_by(
                Product.site
            ).order_by(
                desc('deal_count')
            ).limit(limit).all()
            
            retailers = []
            for r in results:
                retailers.append({
                    "retailer": r.site,
                    "deal_count": r.deal_count,
                    "total_savings": float(r.total_savings or 0),
                    "average_discount": float(r.avg_discount or 0)
                })
            
            return retailers
            
        except Exception as e:
            logger.error(f"Error getting best retailers: {e}")
            return []

    @staticmethod
    def get_price_drop_statistics(db: Session, days: int = 30) -> Dict:
        """Get price drop statistics."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get all products with price history
            products = db.query(Product).filter(Product.is_active == True).all()
            
            total_products = len(products)
            products_with_drops = 0
            total_drop_amount = 0
            total_drop_percent = 0
            biggest_drop = {"product": None, "amount": 0, "percent": 0}
            
            for product in products:
                prices = db.query(PriceHistory).filter(
                    PriceHistory.product_id == product.id,
                    PriceHistory.created_at >= cutoff_date
                ).order_by(PriceHistory.created_at.asc()).all()
                
                if len(prices) < 2:
                    continue
                
                first_price = float(prices[0].price)
                last_price = float(prices[-1].price)
                
                if last_price < first_price:
                    products_with_drops += 1
                    drop_amount = first_price - last_price
                    drop_percent = (drop_amount / first_price) * 100
                    
                    total_drop_amount += drop_amount
                    total_drop_percent += drop_percent
                    
                    if drop_amount > biggest_drop["amount"]:
                        biggest_drop = {
                            "product": product.name,
                            "product_id": product.id,
                            "amount": drop_amount,
                            "percent": drop_percent,
                            "old_price": first_price,
                            "new_price": last_price
                        }
            
            avg_drop_amount = total_drop_amount / products_with_drops if products_with_drops > 0 else 0
            avg_drop_percent = total_drop_percent / products_with_drops if products_with_drops > 0 else 0
            
            return {
                "total_products_tracked": total_products,
                "products_with_price_drops": products_with_drops,
                "drop_rate_percent": (products_with_drops / total_products * 100) if total_products > 0 else 0,
                "average_drop_amount": round(avg_drop_amount, 2),
                "average_drop_percent": round(avg_drop_percent, 2),
                "biggest_drop": biggest_drop if biggest_drop["product"] else None,
                "period_days": days
            }
            
        except Exception as e:
            logger.error(f"Error calculating price drop statistics: {e}")
            return {
                "total_products_tracked": 0,
                "products_with_price_drops": 0,
                "drop_rate_percent": 0,
                "average_drop_amount": 0,
                "average_drop_percent": 0,
                "biggest_drop": None,
                "period_days": days
            }

    @staticmethod
    def get_user_dashboard(db: Session, user_id: int, days: int = 30) -> Dict:
        """Get comprehensive dashboard for a user."""
        try:
            # User's watchlist stats
            watchlist_count = db.query(func.count(Watchlist.id)).filter(
                Watchlist.user_id == user_id
            ).scalar()
            
            # User's potential savings (watchlist items with deals)
            user_savings = db.query(
                func.sum(Deal.savings).label('potential_savings')
            ).join(
                Watchlist, Deal.product_id == Watchlist.product_id
            ).filter(
                Watchlist.user_id == user_id,
                Deal.is_active == True
            ).first()
            
            # User's watchlist items at target price
            at_target = db.query(func.count(Watchlist.id)).filter(
                Watchlist.user_id == user_id,
                Watchlist.target_price.isnot(None)
            ).join(
                Product, Watchlist.product_id == Product.id
            ).join(
                PriceHistory, Product.id == PriceHistory.product_id
            ).filter(
                PriceHistory.price <= Watchlist.target_price
            ).scalar()
            
            return {
                "watchlist_count": watchlist_count or 0,
                "potential_savings": float(user_savings.potential_savings or 0),
                "items_at_target_price": at_target or 0,
                "total_savings": AnalyticsDashboard.get_total_savings(db, user_id, days),
                "most_tracked": AnalyticsDashboard.get_most_tracked_products(db, limit=5),
                "best_retailers": AnalyticsDashboard.get_best_retailers(db, days, limit=5),
                "price_drops": AnalyticsDashboard.get_price_drop_statistics(db, days)
            }
            
        except Exception as e:
            logger.error(f"Error generating user dashboard: {e}")
            return {}

    @staticmethod
    def get_global_dashboard(db: Session, days: int = 30) -> Dict:
        """Get global analytics dashboard."""
        try:
            # Total products tracked
            total_products = db.query(func.count(Product.id)).filter(
                Product.is_active == True
            ).scalar()
            
            # Total active deals
            total_deals = db.query(func.count(Deal.id)).filter(
                Deal.is_active == True
            ).scalar()
            
            # Total users with watchlists
            total_users = db.query(func.count(func.distinct(Watchlist.user_id))).scalar()
            
            return {
                "total_products_tracked": total_products or 0,
                "total_active_deals": total_deals or 0,
                "total_users_tracking": total_users or 0,
                "total_savings": AnalyticsDashboard.get_total_savings(db, None, days),
                "most_tracked_products": AnalyticsDashboard.get_most_tracked_products(db, limit=10),
                "best_retailers": AnalyticsDashboard.get_best_retailers(db, days, limit=10),
                "price_drop_statistics": AnalyticsDashboard.get_price_drop_statistics(db, days)
            }
            
        except Exception as e:
            logger.error(f"Error generating global dashboard: {e}")
            return {}
