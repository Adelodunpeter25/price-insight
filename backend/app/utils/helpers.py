"""Utility helper functions."""

import re
from decimal import Decimal
from typing import Optional
from urllib.parse import urlparse


def validate_url(url: str) -> bool:
    """Validate if URL is properly formatted."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def normalize_url(url: str) -> str:
    """Normalize URL by removing query parameters and fragments."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"


def calculate_discount_percentage(original_price: Decimal, current_price: Decimal) -> Decimal:
    """Calculate discount percentage."""
    if original_price <= 0:
        return Decimal("0")
    return ((original_price - current_price) / original_price) * 100


def extract_price_from_text(text: str) -> Optional[Decimal]:
    """Extract price from text using regex."""
    # Match patterns like $19.99, £25.50, €30.00
    pattern = r"[£$€]?(\d+(?:,\d{3})*(?:\.\d{2})?)"
    match = re.search(pattern, text.replace(",", ""))
    if match:
        return Decimal(match.group(1))
    return None


def is_valid_deal(discount_percent: Decimal, min_discount: Decimal = Decimal("5")) -> bool:
    """Check if discount percentage qualifies as a deal."""
    return discount_percent >= min_discount
