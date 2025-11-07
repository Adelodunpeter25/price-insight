"""Integration tests for travel endpoints."""

import unittest
from datetime import date
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


class TestTravelIntegration(unittest.TestCase):
    """Test travel API integration."""

    def setUp(self):
        """Set up test client."""
        self.client = TestClient(app)

    @patch('app.core.deps.get_database_session')
    def test_create_flight_endpoint(self, mock_db):
        """Test flight creation endpoint."""
        mock_db.return_value.__aenter__.return_value = mock_db
        
        flight_data = {
            "origin": "NYC",
            "destination": "LAX", 
            "departure_date": "2024-12-01",
            "flight_class": "economy",
            "passengers": 1,
            "url": "https://example.com/flight",
            "site": "example"
        }
        
        with patch('app.travel.services.travel_service.TravelService.create_flight') as mock_create:
            mock_flight = type('Flight', (), {
                'id': 1, 'origin': 'NYC', 'destination': 'LAX',
                'departure_date': date(2024, 12, 1), 'return_date': None,
                'airline': None, 'flight_class': 'economy', 'price': 0.0,
                'currency': 'USD', 'url': 'https://example.com/flight',
                'site': 'example', 'passengers': 1, 'is_tracked': True,
                'created_at': '2024-01-01T00:00:00Z', 'updated_at': '2024-01-01T00:00:00Z'
            })()
            mock_create.return_value = mock_flight
            
            response = self.client.post("/api/travel/flights", json=flight_data)
            
            self.assertEqual(response.status_code, 201)

    @patch('app.core.deps.get_database_session')
    def test_list_deals_endpoint(self, mock_db):
        """Test deals listing endpoint."""
        mock_db.return_value.__aenter__.return_value = mock_db
        
        with patch('app.travel.services.deal_service.TravelDealService.get_active_deals') as mock_deals:
            mock_deals.return_value = []
            
            response = self.client.get("/api/travel/deals")
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('items', data)
            self.assertEqual(data['items'], [])

    @patch('app.core.deps.get_database_session')
    def test_create_alert_rule_endpoint(self, mock_db):
        """Test alert rule creation endpoint."""
        mock_session = mock_db.return_value.__aenter__.return_value
        mock_session.add = lambda x: None
        mock_session.commit = lambda: None
        mock_session.refresh = lambda x: setattr(x, 'id', 1)
        
        alert_data = {
            "flight_id": 1,
            "rule_type": "price_drop",
            "percentage_threshold": 10.0,
            "notification_method": "console"
        }
        
        with patch('app.travel.models.travel_alert.TravelAlertRule') as mock_rule_class:
            mock_rule = type('TravelAlertRule', (), {
                'id': 1, 'flight_id': 1, 'hotel_id': None,
                'rule_type': 'price_drop', 'threshold_value': None,
                'percentage_threshold': 10.0, 'notification_method': 'console',
                'created_at': '2024-01-01T00:00:00Z', 'is_active': True
            })()
            mock_rule_class.return_value = mock_rule
            
            response = self.client.post("/api/travel/alerts/rules", json=alert_data)
            
            self.assertEqual(response.status_code, 201)