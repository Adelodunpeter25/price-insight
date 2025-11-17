"""Travel scraping and alert jobs."""

import logging
from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from app.core.database import AsyncSessionLocal
from app.core.services.email_service import email_service
from app.travel.models.flight import Flight
from app.travel.models.hotel import Hotel
from app.travel.models.watchlist import TravelWatchlist
from app.travel.services.deal_detector import TravelDealDetector
from app.travel.services.price_analytics import TravelPriceAnalytics

logger = logging.getLogger(__name__)


async def scrape_tracked_travel_items():
    """Scrape all tracked flights and hotels."""
    async with AsyncSessionLocal() as db:
        try:
            # Get tracked flights
            flights = db.query(Flight).filter(Flight.is_tracked == 1, Flight.is_active == True).all()
            logger.info(f"Found {len(flights)} flights to scrape")

            # Get tracked hotels
            hotels = db.query(Hotel).filter(Hotel.is_tracked == 1, Hotel.is_active == True).all()
            logger.info(f"Found {len(hotels)} hotels to scrape")

            # TODO: Implement actual scraping logic
            # This would involve:
            # 1. Get appropriate scraper for each URL
            # 2. Scrape current price
            # 3. Update price in database
            # 4. Add price history record

            logger.info("Travel scraping job completed")

        except Exception as e:
            logger.error(f"Error in travel scraping job: {e}")


async def detect_travel_deals():
    """Detect deals for flights and hotels."""
    async with AsyncSessionLocal() as db:
        try:
            detector = TravelDealDetector()
            deals = detector.detect_deals(db)
            
            logger.info(f"Detected {len(deals)} travel deals")
            
            # TODO: Send notifications to users with matching preferences
            
        except Exception as e:
            logger.error(f"Error in travel deal detection: {e}")


async def check_travel_watchlist_alerts():
    """Check watchlist items for price alerts."""
    async with AsyncSessionLocal() as db:
        try:
            watchlist_items = (
                db.query(TravelWatchlist)
                .filter(TravelWatchlist.is_active == True)
                .all()
            )
            
            alerts_sent = 0
            
            for item in watchlist_items:
                try:
                    current_price = None
                    item_name = ""
                    
                    if item.flight_id and item.flight:
                        current_price = float(item.flight.price)
                        item_name = f"{item.flight.origin}-{item.flight.destination} flight"
                    elif item.hotel_id and item.hotel:
                        current_price = float(item.hotel.total_price)
                        item_name = f"{item.hotel.name} hotel"
                    
                    if not current_price:
                        continue
                    
                    # Check target price alert
                    if (item.alert_on_target and 
                        item.target_price and 
                        current_price <= float(item.target_price)):
                        
                        await email_service.send_price_alert(
                            to=item.user.email,
                            product_name=item_name,
                            old_price=float(item.target_price),
                            new_price=current_price,
                            currency="₦"
                        )
                        alerts_sent += 1
                        logger.info(f"Sent target price alert for {item_name}")
                    
                    # Check price drop alert
                    if item.alert_on_any_drop:
                        # Get previous price from history
                        item_type = "flight" if item.flight_id else "hotel"
                        item_id = item.flight_id or item.hotel_id
                        
                        if item_type == "flight":
                            stats = TravelPriceAnalytics.get_flight_price_stats(db, item_id, 7)
                        else:
                            stats = TravelPriceAnalytics.get_hotel_price_stats(db, item_id, 7)
                        
                        if stats and stats.get('price_drop_percentage', 0) > 5:
                            await email_service.send_price_alert(
                                to=item.user.email,
                                product_name=item_name,
                                old_price=stats['highest_price'],
                                new_price=current_price,
                                currency="₦"
                            )
                            alerts_sent += 1
                            logger.info(f"Sent price drop alert for {item_name}")
                
                except Exception as e:
                    logger.error(f"Error processing watchlist item {item.id}: {e}")
                    continue
            
            logger.info(f"Sent {alerts_sent} travel watchlist alerts")
            
        except Exception as e:
            logger.error(f"Error in travel watchlist alerts: {e}")