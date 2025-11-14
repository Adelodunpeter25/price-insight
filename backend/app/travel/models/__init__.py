"""Travel models."""

from .deal import TravelDeal
from .flight import Flight
from .hotel import Hotel
from .price_history import TravelPriceHistory
from .travel_alert import TravelAlertRule

__all__ = ["Flight", "Hotel", "TravelDeal", "TravelAlertRule", "TravelPriceHistory"]
