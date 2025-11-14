"""Integration tests for complete workflows."""

import unittest
from decimal import Decimal
from unittest.mock import patch

from tests.test_config import BaseTestCase


class TestIntegration(BaseTestCase):
    """Integration tests for complete workflows."""

    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertIn("version", data)

    def test_status_endpoint(self):
        """Test status endpoint."""
        response = self.client.get("/api/status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("scheduler_running", data)
        self.assertIn("total_jobs", data)

    def test_create_product_endpoint(self):
        """Test product creation endpoint."""
        product_data = {
            "name": "Test Product",
            "url": "https://example.com/product",
            "site": "example.com",
            "category": "electronics",
        }

        response = self.client.post("/api/e-commerce/products/", json=product_data)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["name"], "Test Product")
        self.assertEqual(data["site"], "example.com")

    def test_list_products_endpoint(self):
        """Test product listing endpoint."""
        response = self.client.get("/api/e-commerce/products/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("items", data)
        self.assertIn("total", data)
        self.assertIn("page", data)

    def test_list_deals_endpoint(self):
        """Test deals listing endpoint."""
        response = self.client.get("/api/e-commerce/deals")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("items", data)
        self.assertIn("total", data)

    def test_list_alerts_endpoint(self):
        """Test alerts listing endpoint."""
        response = self.client.get("/api/e-commerce/alerts")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("items", data)
        self.assertIn("total", data)

    def test_create_alert_rule_invalid_product(self):
        """Test creating alert rule for non-existent product."""
        rule_data = {
            "product_id": 99999,
            "rule_type": "price_drop",
            "percentage_threshold": 10.0,
            "notification_method": "console",
        }

        response = self.client.post("/api/e-commerce/alerts/rules", json=rule_data)
        self.assertEqual(response.status_code, 404)

    @patch("app.ecommerce.services.scrapers.amazon.AmazonScraper.scrape")
    async def test_scraping_workflow(self, mock_scrape):
        """Test complete scraping workflow."""
        # Mock scraper response
        mock_scrape.return_value = {
            "name": "Test Product",
            "price": Decimal("19.99"),
            "url": "https://amazon.com/test",
            "availability": "In Stock",
            "site": "amazon",
            "currency": "USD",
        }

        # This would test the complete workflow:
        # 1. Create product
        # 2. Create alert rule
        # 3. Run scraping job
        # 4. Verify alert triggered
        # Note: This requires more complex setup with test database

        self.assertTrue(True)  # Placeholder for now


class TestAPIValidation(BaseTestCase):
    """Test API input validation."""

    def test_create_product_invalid_url(self):
        """Test product creation with invalid URL."""
        product_data = {
            "name": "Test Product",
            "url": "not-a-valid-url",
            "site": "example.com",
        }

        response = self.client.post("/api/e-commerce/products/", json=product_data)
        self.assertEqual(response.status_code, 422)  # Validation error

    def test_create_product_missing_fields(self):
        """Test product creation with missing required fields."""
        product_data = {"name": "Test Product"}  # Missing url and site

        response = self.client.post("/api/e-commerce/products/", json=product_data)
        self.assertEqual(response.status_code, 422)

    def test_pagination_parameters(self):
        """Test pagination parameter validation."""
        # Test invalid page number
        response = self.client.get("/api/e-commerce/products/?page=0")
        self.assertEqual(response.status_code, 422)

        # Test invalid page size
        response = self.client.get("/api/e-commerce/products/?size=1000")
        self.assertEqual(response.status_code, 422)

        # Test valid parameters
        response = self.client.get("/api/e-commerce/products/?page=1&size=10")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
