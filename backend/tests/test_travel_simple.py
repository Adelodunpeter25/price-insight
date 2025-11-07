"""Simple travel tests that work."""

import unittest
from unittest.mock import AsyncMock, MagicMock

from app.travel.services.deal_service import TravelDealService


class TestTravelDealServiceSimple(unittest.IsolatedAsyncioTestCase):
    """Simple travel deal service tests."""

    def setUp(self):
        """Set up test."""
        self.mock_db = AsyncMock()
        self.service = TravelDealService(self.mock_db)

    async def test_get_active_deals_empty(self):
        """Test getting empty active deals."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        self.mock_db.execute = AsyncMock(return_value=mock_result)

        result = await self.service.get_active_deals()

        self.assertEqual(result, [])
        self.mock_db.execute.assert_called_once()

    async def test_get_deal_by_id_none(self):
        """Test getting deal by ID returns None."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_db.execute = AsyncMock(return_value=mock_result)

        result = await self.service.get_deal_by_id(999)

        self.assertIsNone(result)
        self.mock_db.execute.assert_called_once()
