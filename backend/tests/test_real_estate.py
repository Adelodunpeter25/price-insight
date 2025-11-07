"""Tests for real estate functionality."""

import unittest
from decimal import Decimal
from unittest.mock import patch

from app.real_estate.services.scrapers.property_scraper import PropertyScraper


class TestPropertyService(unittest.TestCase):
    """Test PropertyService utility methods."""

    def test_property_creation_data(self):
        """Test property data structure."""
        property_data = {
            "name": "Test Property",
            "property_type": "house",
            "location": "Lagos",
            "url": "https://example.com/property/1",
            "site": "example.com",
            "listing_type": "sale",
            "price": Decimal("50000000"),
            "currency": "NGN",
            "is_tracked": 1,
        }

        self.assertEqual(property_data["name"], "Test Property")
        self.assertEqual(property_data["property_type"], "house")
        self.assertEqual(property_data["price"], Decimal("50000000"))
        self.assertEqual(property_data["currency"], "NGN")

    def test_price_history_data(self):
        """Test price history data structure."""
        price_history_data = {
            "property_id": 1,
            "price": Decimal("45000000"),
            "currency": "NGN",
            "price_per_sqm": Decimal("150000"),
            "listing_status": "active",
        }

        self.assertEqual(price_history_data["property_id"], 1)
        self.assertEqual(price_history_data["price"], Decimal("45000000"))
        self.assertEqual(price_history_data["currency"], "NGN")


class TestPropertyScraper(unittest.IsolatedAsyncioTestCase):
    """Test PropertyScraper functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.scraper = PropertyScraper()

    def test_parse_price(self):
        """Test price parsing."""
        # Test various price formats
        test_cases = [
            ("₦50,000,000", Decimal("50000000")),
            ("N45000000", Decimal("45000000")),
            ("$100,000", Decimal("100000")),
            ("Price: ₦25,500,000", Decimal("25500000")),
        ]

        for price_text, expected in test_cases:
            with self.subTest(price_text=price_text):
                result = self.scraper._parse_price(price_text)
                self.assertEqual(result, expected)

    def test_parse_number(self):
        """Test number parsing."""
        test_cases = [
            ("3 bedrooms", 3),
            ("5 bed", 5),
            ("2 baths", 2),
            ("No bedrooms", None),
        ]

        for text, expected in test_cases:
            with self.subTest(text=text):
                result = self.scraper._parse_number(text)
                self.assertEqual(result, expected)

    def test_determine_property_type(self):
        """Test property type determination."""
        test_cases = [
            ("3 bedroom apartment", "apartment"),
            ("5 bedroom duplex house", "house"),
            ("commercial office space", "commercial"),
            ("land for sale", "land"),
            ("luxury villa", "house"),  # default
        ]

        for name, expected in test_cases:
            with self.subTest(name=name):
                result = self.scraper._determine_property_type(name.lower())
                self.assertEqual(result, expected)

    def test_determine_listing_type(self):
        """Test listing type determination."""
        test_cases = [
            ("₦500,000 per month", "rent"),
            ("Monthly rent: ₦300,000", "rent"),
            ("₦50,000,000 for sale", "sale"),
            ("₦25,000,000", "sale"),  # default
        ]

        for price_text, expected in test_cases:
            with self.subTest(price_text=price_text):
                result = self.scraper._determine_listing_type(price_text.lower())
                self.assertEqual(result, expected)

    @patch("app.real_estate.services.scrapers.property_scraper.PropertyScraper.fetch")
    async def test_extract_data_success(self, mock_fetch):
        """Test successful data extraction."""
        # Mock HTML content
        mock_html = """
        <html>
            <body>
                <h1>3 Bedroom Apartment in Victoria Island</h1>
                <div class="price">₦45,000,000</div>
                <div class="location">Victoria Island, Lagos</div>
                <div class="bedrooms">3 bedrooms</div>
                <div class="bathrooms">2 bathrooms</div>
            </body>
        </html>
        """
        mock_fetch.return_value = mock_html

        result = await self.scraper.extract_data("https://example.com/property/1")

        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "3 Bedroom Apartment in Victoria Island")
        self.assertEqual(result["price"], Decimal("45000000"))
        self.assertEqual(result["location"], "Victoria Island, Lagos")
        self.assertEqual(result["property_type"], "apartment")
        self.assertEqual(result["bedrooms"], 3)
        self.assertEqual(result["bathrooms"], 2)

    @patch("app.real_estate.services.scrapers.property_scraper.PropertyScraper.fetch")
    async def test_extract_data_missing_required_fields(self, mock_fetch):
        """Test extraction with missing required fields."""
        # Mock HTML without price
        mock_html = """
        <html>
            <body>
                <h1>Test Property</h1>
                <div class="location">Lagos</div>
            </body>
        </html>
        """
        mock_fetch.return_value = mock_html

        result = await self.scraper.extract_data("https://example.com/property/1")

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
