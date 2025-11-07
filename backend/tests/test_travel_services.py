"""Tests for travel services."""

import unittest
from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock

from app.travel.services.deal_service import TravelDealService
from app.travel.services.travel_service import TravelService


class TestTravelService(unittest.IsolatedAsyncioTestCase):
    """Test travel service."""

    def setUp(self):
        """Set up test."""
        self.mock_db = AsyncMock()
        self.service = TravelService(self.mock_db)

    async def test_create_flight(self):
        """Test creating flight."""
        mock_flight = MagicMock()
        mock_flight.id = 1
        self.mock_db.add = MagicMock()
        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()

        result = await self.service.create_flight(
            origin="NYC",
            destination="LAX",
            departure_date=date(2024, 12, 1),
            return_date=None,
            flight_class="economy",
            passengers=1,
            url="https://example.com",
            site="example"
        )

        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()

    async def test_create_hotel(self):
        """Test creating hotel."""
        mock_hotel = MagicMock()
        mock_hotel.id = 1
        self.mock_db.add = MagicMock()
        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()

        result = await self.service.create_hotel(
            name="Test Hotel",
            location="NYC",
            check_in=date(2024, 12, 1),
            check_out=date(2024, 12, 3),
            room_type="standard",
            guests=2,
            url="https://example.com",
            site="example"
        )

        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()


class TestTravelDealService(unittest.IsolatedAsyncioTestCase):
    """Test travel deal service."""

    def setUp(self):
        """Set up test."""
        self.mock_db = AsyncMock()
        self.service = TravelDealService(self.mock_db)

    async def test_create_deal(self):
        """Test creating deal."""
        mock_deal = MagicMock()
        mock_deal.id = 1
        self.mock_db.add = MagicMock()
        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()

        result = await self.service.create_deal(
            flight_id=1,
            discount_percent=20.0,
            original_price=500.0,
            deal_price=400.0,
            deal_source="test"
        )

        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()

    async def test_get_active_deals(self):
        """Test getting active deals."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        self.mock_db.execute = AsyncMock(return_value=mock_result)

        result = await self.service.get_active_deals()

        self.mock_db.execute.assert_called_once()
        self.assertEqual(result, [])