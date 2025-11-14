"""Script to add database indexes for performance optimization."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text

from app.core.database import engine


async def add_indexes():
    """Add indexes to frequently queried columns."""
    
    indexes = [
        # Price history - frequently queried by product_id and created_at for analytics
        "CREATE INDEX IF NOT EXISTS idx_price_history_product_created ON price_history(product_id, created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_price_history_created ON price_history(created_at DESC)",
        
        # Deals - queried by product_id, deal_type, and date ranges
        "CREATE INDEX IF NOT EXISTS idx_deals_product_type ON deals(product_id, deal_type)",
        "CREATE INDEX IF NOT EXISTS idx_deals_active_dates ON deals(deal_start_date, deal_end_date)",
        "CREATE INDEX IF NOT EXISTS idx_deals_discount ON deals(discount_percent DESC)",
        
        # Watchlists - queried by user_id and product_id
        "CREATE INDEX IF NOT EXISTS idx_watchlists_user_product ON watchlists(user_id, product_id)",
        "CREATE INDEX IF NOT EXISTS idx_watchlists_user_id ON watchlists(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_watchlists_product_id ON watchlists(product_id)",
        
        # Alert rules - queried by product_id and rule_type
        "CREATE INDEX IF NOT EXISTS idx_alert_rules_product_type ON alert_rules(product_id, rule_type)",
        
        # Alert history - queried by alert_rule_id and created_at
        "CREATE INDEX IF NOT EXISTS idx_alert_history_rule_created ON alert_history(alert_rule_id, created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_alert_history_product_created ON alert_history(product_id, created_at DESC)",
        
        # Products - composite indexes for common queries
        "CREATE INDEX IF NOT EXISTS idx_products_site_category ON products(site, category)",
        "CREATE INDEX IF NOT EXISTS idx_products_tracked_created ON products(is_tracked, created_at DESC)",
        
        # Users - email already indexed, add is_verified for filtering
        "CREATE INDEX IF NOT EXISTS idx_users_verified_created ON users(is_verified, created_at DESC)",
    ]
    
    for idx_sql in indexes:
        async with engine.begin() as conn:
            try:
                await conn.execute(text(idx_sql))
                print(f"✓ Created: {idx_sql.split('idx_')[1].split(' ')[0]}")
            except Exception as e:
                print(f"✗ Failed: {str(e)}")


if __name__ == "__main__":
    print("Adding database indexes...")
    asyncio.run(add_indexes())
    print("Done!")
