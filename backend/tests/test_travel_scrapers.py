"""Tests for travel scrapers."""

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.travel.services.scrapers.flight_scraper import FlightScraper
from app.travel.services.scrapers.hotel_scraper import HotelScraper


class TestFlightScraper(unittest.IsolatedAsyncioTestCase):
    """Test flight scraper."""

    def setUp(self):
        """Set up test."""
        self.scraper = FlightScraper()

    @patch("httpx.AsyncClient")
    async def test_fetch_success(self, mock_client_class):
        """Test successful fetch."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Flight data</body></html>"

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        result = await self.scraper.fetch("https://example.com")
        self.assertEqual(result.status_code, 200)

    def test_parse_html(self):
        """Test HTML parsing."""
        html = "<html><body><div class='price'>$500</div></body></html>"

        soup = self.scraper.parse(html)

        self.assertIsNotNone(soup)
        self.assertEqual(soup.find("div", class_="price").text, "$500")

    def test_extract_data(self):
        """Test data extraction."""
        html = "<html><body><div class='price'>$500</div></body></html>"
        soup = self.scraper.parse(html)

        data = self.scraper.extract_data(soup, "https://example.com")

        self.assertIsInstance(data, dict)
        self.assertIn("price", data)


class TestHotelScraper(unittest.IsolatedAsyncioTestCase):
    """Test hotel scraper."""

    def setUp(self):
        """Set up test."""
        self.scraper = HotelScraper()

    @patch("httpx.AsyncClient")
    async def test_fetch_success(self, mock_client_class):
        """Test successful fetch."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Hotel data</body></html>"

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        result = await self.scraper.fetch("https://example.com")
        self.assertEqual(result.status_code, 200)

    def test_parse_html(self):
        """Test HTML parsing."""
        html = "<html><body><div class='price'>$200/night</div></body></html>"

        soup = self.scraper.parse(html)

        self.assertIsNotNone(soup)
        self.assertEqual(soup.find("div", class_="price").text, "$200/night")

    def test_extract_data(self):
        """Test data extraction."""
        html = "<html><body><div class='price'>$200</div></body></html>"
        soup = self.scraper.parse(html)

        data = self.scraper.extract_data(soup, "https://example.com")

        self.assertIsInstance(data, dict)
        self.assertIn("price_per_night", data)
