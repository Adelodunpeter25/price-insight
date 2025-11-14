"""Centralized deal detection manager."""

import logging
from typing import Dict, List

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from app.ecommerce.services.deal_detector import EcommerceDealDetector
from app.real_estate.services.deal_detector import RealEstateDealDetector
from app.travel.services.deal_detector import TravelDealDetector
from app.utilities.services.deal_detector import UtilityDealDetector


class DealDetectionManager:
    """Centralized manager for deal detection across all categories."""

    def __init__(self):
        """Initialize deal detectors for all categories."""
        self.ecommerce_detector = EcommerceDealDetector()
        self.travel_detector = TravelDealDetector()
        self.real_estate_detector = RealEstateDealDetector()
        self.utility_detector = UtilityDealDetector()

    def detect_all_deals(self, db: Session) -> Dict[str, List]:
        """Run deal detection for all categories."""
        results = {}

        try:
            logger.info("Starting comprehensive deal detection")

            # E-commerce deals
            ecommerce_deals = self.ecommerce_detector.detect_deals(db)
            results["ecommerce"] = ecommerce_deals
            logger.info(f"Detected {len(ecommerce_deals)} e-commerce deals")

            # Travel deals
            travel_deals = self.travel_detector.detect_deals(db)
            results["travel"] = travel_deals
            logger.info(f"Detected {len(travel_deals)} travel deals")

            # Real estate deals
            real_estate_deals = self.real_estate_detector.detect_deals(db)
            results["real_estate"] = real_estate_deals
            logger.info(f"Detected {len(real_estate_deals)} real estate deals")

            # Utility deals
            utility_deals = self.utility_detector.detect_deals(db)
            results["utilities"] = utility_deals
            logger.info(f"Detected {len(utility_deals)} utility deals")

            total_deals = sum(len(deals) for deals in results.values())
            logger.info(f"Total deals detected: {total_deals}")

            db.commit()

        except Exception as e:
            logger.error(f"Error during deal detection: {e}")
            db.rollback()

        return results

    def detect_category_deals(self, db: Session, category: str) -> List:
        """Run deal detection for specific category."""
        try:
            if category == "ecommerce":
                deals = self.ecommerce_detector.detect_deals(db)
            elif category == "travel":
                deals = self.travel_detector.detect_deals(db)
            elif category == "real_estate":
                deals = self.real_estate_detector.detect_deals(db)
            elif category == "utilities":
                deals = self.utility_detector.detect_deals(db)
            else:
                logger.warning(f"Unknown category: {category}")
                return []

            logger.info(f"Detected {len(deals)} deals for {category}")
            db.commit()
            return deals

        except Exception as e:
            logger.error(f"Error detecting {category} deals: {e}")
            db.rollback()
            return []


# Global deal detection manager
deal_manager = DealDetectionManager()
