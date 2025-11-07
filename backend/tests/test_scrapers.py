"""Unit tests for scraper functionality."""

import unittest
from decimal import Decimal
from unittest.mock import patch

from app.ecommerce.services.scraper_base import BaseScraper
from app.ecommerce.services.scrapers.amazon import AmazonScraper
from app.ecommerce.services.scrapers.generic import GenericScraper


class TestScraper(BaseScraper):
    """Test implementation of BaseScraper."""

    def extract_data(self, soup, url: str) -> dict:
        """Test implementation of extract_data."""
        return {
            "name": "Test Product",
            "price": Decimal("19.99"),
            "availability": "In Stock",
            "currency": "USD",
        }


class TestBaseScraper(unittest.TestCase):
    """Test base scraper functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.scraper = TestScraper()

    def test_init(self):
        """Test scraper initialization."""
        self.assertEqual(self.scraper.timeout, 30)
        self.assertEqual(self.scraper.max_retries, 3)
        self.assertIsNone(self.scraper.session)

    def test_parse_html(self):
        """Test HTML parsing."""
        html = "<html><body><h1>Test</h1></body></html>"
        soup = self.scraper.parse(html)
        self.assertEqual(soup.find("h1").text, "Test")

    def test_validate_data_valid(self):
        """Test data validation with valid data."""
        data = {"name": "Test Product", "price": 19.99, "url": "http://example.com"}
        self.assertTrue(self.scraper.validate_data(data))

    def test_validate_data_invalid(self):
        """Test data validation with invalid data."""
        data = {"name": "Test Product", "price": 19.99}  # Missing url
        self.assertFalse(self.scraper.validate_data(data))


class TestAmazonScraper(unittest.TestCase):
    """Test Amazon scraper functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.scraper = AmazonScraper()

    @patch("app.ecommerce.services.scraper_base.BaseScraper.fetch")
    async def test_extract_data_success(self, mock_fetch):
        """Test successful data extraction."""
        mock_html = """
        <html>
            <body>
                <span id="productTitle">Test Product</span>
                <span class="a-price-whole">19</span>
                <span id="availability">In Stock</span>
            </body>
        </html>
        """
        mock_fetch.return_value = mock_html

        result = await self.scraper.extract_data("http://amazon.com/test")

        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Test Product")
        self.assertEqual(result["site"], "amazon")

    @patch("app.ecommerce.services.scraper_base.BaseScraper.fetch")
    async def test_extract_data_no_html(self, mock_fetch):
        """Test extraction with no HTML returned."""
        mock_fetch.return_value = None

        result = await self.scraper.extract_data("http://amazon.com/test")

        self.assertIsNone(result)


class TestGenericScraper(unittest.TestCase):
    """Test generic scraper functionality."""

    def setUp(self):
        """Set up test fixtures."""
        selectors = {
            "name": [".product-title", "h1"],
            "price": [".price", ".cost"],
            "availability": [".stock"],
        }
        self.scraper = GenericScraper(selectors)

    @patch("app.ecommerce.services.scraper_base.BaseScraper.fetch")
    async def test_extract_data_success(self, mock_fetch):
        """Test successful data extraction with generic scraper."""
        mock_html = """
        <html>
            <body>
                <h1>Generic Product</h1>
                <span class="price">$25.99</span>
                <span class="stock">Available</span>
            </body>
        </html>
        """
        mock_fetch.return_value = mock_html

        result = await self.scraper.extract_data("http://example.com/product")

        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Generic Product")
        self.assertEqual(result["availability"], "Available")


if __name__ == "__main__":
    unittest.main()
