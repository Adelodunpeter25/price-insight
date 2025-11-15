"""Real estate models."""

from .alert import PropertyAlertHistory, PropertyAlertRule
from .deal import PropertyDeal
from .deal_preference import PropertyDealPreference
from .price_history import PropertyPriceHistory
from .property import Property
from .watchlist import PropertyWatchlist

__all__ = [
    "Property",
    "PropertyPriceHistory",
    "PropertyDeal",
    "PropertyAlertRule",
    "PropertyAlertHistory",
    "PropertyWatchlist",
    "PropertyDealPreference",
]
