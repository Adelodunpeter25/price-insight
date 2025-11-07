"""Currency conversion utilities."""

import re
from decimal import Decimal
from typing import Optional, Tuple

import httpx
from loguru import logger

from app.core.config import settings


class CurrencyConverter:
    """Currency converter to Naira."""

    def __init__(self):
        """Initialize converter."""
        self.exchange_rates = {}
        self.api_key = getattr(settings, 'exchange_rate_api_key', None)
        self.base_url = "https://v6.exchangerate-api.com/v6"

    async def get_exchange_rates(self) -> dict:
        """Fetch current exchange rates."""
        if not self.api_key:
            logger.warning("Exchange rate API key not configured")
            return self._get_fallback_rates()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/{self.api_key}/latest/NGN"
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("result") == "success":
                    # Convert to rates FROM other currencies TO NGN
                    rates = {}
                    for currency, rate in data["conversion_rates"].items():
                        if rate > 0:
                            rates[currency] = 1 / rate  # Invert to get rate to NGN
                    
                    self.exchange_rates = rates
                    logger.info("Exchange rates updated successfully")
                    return rates
                else:
                    logger.error(f"Exchange rate API error: {data.get('error-type')}")
                    return self._get_fallback_rates()
                    
        except Exception as e:
            logger.error(f"Failed to fetch exchange rates: {e}")
            return self._get_fallback_rates()

    def _get_fallback_rates(self) -> dict:
        """Fallback exchange rates (approximate)."""
        return {
            "USD": 750.0,
            "EUR": 820.0,
            "GBP": 950.0,
            "JPY": 5.2,
            "CAD": 550.0,
            "AUD": 490.0,
            "CHF": 830.0,
            "CNY": 105.0,
            "NGN": 1.0,
        }

    def extract_price_and_currency(self, price_text: str) -> Tuple[Optional[Decimal], str]:
        """Extract price and currency from text."""
        if not price_text:
            return None, "NGN"

        # Clean the text
        price_text = price_text.strip().replace(",", "").replace(" ", "")
        
        # Currency symbols and codes mapping
        currency_patterns = {
            r"₦|NGN": "NGN",
            r"\$|USD": "USD", 
            r"€|EUR": "EUR",
            r"£|GBP": "GBP",
            r"¥|JPY": "JPY",
            r"C\$|CAD": "CAD",
            r"A\$|AUD": "AUD",
            r"CHF": "CHF",
            r"¥|CNY": "CNY",
        }
        
        # Find currency
        currency = "NGN"  # Default
        for pattern, curr_code in currency_patterns.items():
            if re.search(pattern, price_text, re.IGNORECASE):
                currency = curr_code
                break
        
        # Extract numeric value
        price_match = re.search(r"[\d,]+\.?\d*", price_text)
        if not price_match:
            return None, currency
            
        try:
            price_value = Decimal(price_match.group().replace(",", ""))
            return price_value, currency
        except Exception as e:
            logger.error(f"Failed to parse price '{price_text}': {e}")
            return None, currency

    async def convert_to_naira(self, amount: Decimal, from_currency: str) -> Decimal:
        """Convert amount from currency to Naira."""
        if from_currency == "NGN":
            return amount
            
        # Ensure we have exchange rates
        if not self.exchange_rates:
            await self.get_exchange_rates()
            
        rate = self.exchange_rates.get(from_currency.upper())
        if not rate:
            logger.warning(f"No exchange rate found for {from_currency}, using fallback")
            fallback_rates = self._get_fallback_rates()
            rate = fallback_rates.get(from_currency.upper(), 1.0)
            
        converted = amount * Decimal(str(rate))
        logger.info(f"Converted {amount} {from_currency} to {converted:.2f} NGN")
        return converted.quantize(Decimal('0.01'))

    async def normalize_price(self, price_text: str) -> Optional[Decimal]:
        """Extract price and convert to Naira."""
        price, currency = self.extract_price_and_currency(price_text)
        
        if price is None:
            return None
            
        return await self.convert_to_naira(price, currency)


# Global converter instance
currency_converter = CurrencyConverter()