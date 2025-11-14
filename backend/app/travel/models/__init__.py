"""Travel models."""

from .deal import TravelDeal
from .flight import Flight
from .hotel import Hotel
from .travel_alert import TravelAlertRule
from .price_history import TravelPriceHistory

__all__ = ["Flight", "Hotel", "TravelDeal", "TravelAlertRule", "TravelPriceHistory"]
