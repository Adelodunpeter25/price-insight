"""Tests for travel alerts."""

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.travel.services.travel_alert_service import TravelAlertService


class TestTravelAlertService(unittest.IsolatedAsyncioTestCase):
    """Test travel alert service."""

    def setUp(self):
        """Set up test."""
        self.mock_db = AsyncMock()
        self.service = TravelAlertService(self.mock_db)

    async def test_get_flight_alert_rules(self):
        """Test getting flight alert rules."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        self.mock_db.execute = AsyncMock(return_value=mock_result)
        
        result = await self.service.get_flight_alert_rules(1)
        
        self.assertEqual(result, [])
        self.mock_db.execute.assert_called_once()

    async def test_get_hotel_alert_rules(self):
        """Test getting hotel alert rules."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        self.mock_db.execute = AsyncMock(return_value=mock_result)
        
        result = await self.service.get_hotel_alert_rules(1)
        
        self.assertEqual(result, [])
        self.mock_db.execute.assert_called_once()

    async def test_send_alert_notification(self):
        """Test sending alert notification."""
        # This method exists and should not raise exception
        await self.service.send_alert_notification(
            "Test alert message", "console"
        )
        # No assertion needed - just testing it doesn't crash