"""Unit tests for service layer functionality."""

import unittest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from app.ecommerce.models import Product
from app.ecommerce.services.product_service import ProductService


class TestProductService(unittest.TestCase):
    """Test product service functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_db = AsyncMock()
        self.service = ProductService(self.mock_db)

    async def test_get_or_create_product_existing(self):
        """Test getting existing product."""
        # Mock existing product
        existing_product = Product(
            id=1, name="Test Product", url="http://example.com", site="example"
        )

        # Mock database query result
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_product
        self.mock_db.execute.return_value = mock_result

        result = await self.service.get_or_create_product(
            url="http://example.com", name="Test Product", site="example"
        )

        self.assertEqual(result, existing_product)
        self.mock_db.add.assert_not_called()

    async def test_get_or_create_product_new(self):
        """Test creating new product."""
        # Mock no existing product
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_db.execute.return_value = mock_result

        # Mock refresh to set ID
        async def mock_refresh(product):
            product.id = 1

        self.mock_db.refresh = mock_refresh

        result = await self.service.get_or_create_product(
            url="http://example.com", name="New Product", site="example"
        )

        self.assertEqual(result.name, "New Product")
        self.assertEqual(result.url, "http://example.com")
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()

    async def test_add_price_history(self):
        """Test adding price history entry."""

        # Mock refresh to set ID
        async def mock_refresh(price_entry):
            price_entry.id = 1

        self.mock_db.refresh = mock_refresh

        result = await self.service.add_price_history(
            product_id=1, price=Decimal("19.99"), currency="USD"
        )

        self.assertEqual(result.product_id, 1)
        self.assertEqual(result.price, Decimal("19.99"))
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()

    async def test_get_products_to_track(self):
        """Test getting products to track."""
        # Mock products
        products = [
            Product(id=1, name="Product 1", is_tracked=True, is_active=True),
            Product(id=2, name="Product 2", is_tracked=True, is_active=True),
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = products
        self.mock_db.execute.return_value = mock_result

        result = await self.service.get_products_to_track()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].name, "Product 1")


if __name__ == "__main__":
    unittest.main()
