"""
Integration tests for the API endpoints.
Run with: pytest tests/
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert "service" in response.json()
        assert "version" in response.json()
    
    def test_health_check(self):
        """Test overall health check."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "services" in data
    
    def test_api_info(self):
        """Test API info endpoint."""
        response = client.get("/api/info")
        assert response.status_code == 200
        data = response.json()
        assert "features" in data
        assert "ml_models" in data


class TestPricingEndpoints:
    """Test pricing prediction endpoints."""
    
    @pytest.fixture
    def valid_pricing_request(self):
        """Valid pricing request fixture."""
        return {
            "current_price": 1000,
            "competitor_price": 950,
            "demand": 200,
            "inventory": 50,
            "conversion_rate": 0.12,
            "promotion": 1,
            "discount_percent": 10,
            "demand_index": 0.75
        }
    
    def test_predict_price(self, valid_pricing_request):
        """Test price prediction endpoint."""
        response = client.post("/api/v1/pricing/predict", json=valid_pricing_request)
        assert response.status_code == 200
        data = response.json()
        assert "recommended_price" in data
        assert "model_used" in data
        assert "confidence_score" in data
    
    def test_predict_price_with_explanation(self, valid_pricing_request):
        """Test price prediction with explanation."""
        response = client.post(
            "/api/v1/pricing/predict-with-explanation",
            json=valid_pricing_request
        )
        assert response.status_code == 200
        data = response.json()
        assert "recommended_price" in data
        assert "feature_importance" in data
        assert "top_factors" in data
        assert "explanation" in data
    
    def test_simulate_revenue(self):
        """Test revenue simulation."""
        request_data = {
            "current_price": 1000,
            "current_demand": 100,
            "proposed_price": 1100,
            "price_elasticity": -1.5
        }
        response = client.post("/api/v1/pricing/simulate-revenue", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "current_revenue" in data
        assert "projected_revenue" in data
        assert "revenue_change_percent" in data
    
    def test_pricing_health(self):
        """Test pricing service health."""
        response = client.get("/api/v1/pricing/health")
        assert response.status_code == 200
        assert response.json()["status"] in ["healthy", "degraded"]


class TestForecastEndpoints:
    """Test demand forecasting endpoints."""
    
    @pytest.fixture
    def valid_forecast_request(self):
        """Valid forecast request fixture."""
        return {
            "product_id": "PROD001",
            "historical_demand": [100, 110, 120, 115, 130, 125, 140],
            "days_ahead": 30,
            "seasonality": "weekly"
        }
    
    def test_forecast_demand(self, valid_forecast_request):
        """Test demand forecast endpoint."""
        response = client.post("/api/v1/forecast/demand", json=valid_forecast_request)
        assert response.status_code == 200
        data = response.json()
        assert "forecasted_demand" in data
        assert "trend" in data
        assert "confidence_interval_lower" in data
        assert "confidence_interval_upper" in data
        assert "prediction_accuracy" in data
    
    def test_demand_insights(self):
        """Test demand insights endpoint."""
        response = client.post(
            "/api/v1/forecast/insights",
            params={
                "product_id": "PROD001",
                "historical_demand": [100, 110, 120, 115, 130, 125, 140]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "average_demand" in data
        assert "peak_demand" in data
    
    def test_inventory_recommendation(self):
        """Test inventory recommendation endpoint."""
        response = client.post(
            "/api/v1/forecast/inventory-recommendation",
            params={
                "product_id": "PROD001",
                "forecasted_demand": [100, 110, 120, 115, 130, 125, 140]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "minimum_stock" in data
        assert "reorder_point" in data
        assert "maximum_stock" in data
    
    def test_forecast_health(self):
        """Test forecast service health."""
        response = client.get("/api/v1/forecast/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestCustomerEndpoints:
    """Test customer segmentation endpoints."""
    
    @pytest.fixture
    def valid_customer_request(self):
        """Valid customer request fixture."""
        return {
            "purchase_frequency": 12,
            "average_order_value": 500,
            "customer_lifetime_value": 6000,
            "loyalty_score": 0.85
        }
    
    def test_segment_customer(self, valid_customer_request):
        """Test customer segmentation endpoint."""
        response = client.post("/api/v1/customer/segment", json=valid_customer_request)
        assert response.status_code == 200
        data = response.json()
        assert "segment" in data
        assert "segment_description" in data
        assert "recommended_discount" in data
    
    def test_churn_prediction(self, valid_customer_request):
        """Test churn prediction endpoint."""
        response = client.post("/api/v1/customer/churn-prediction", json=valid_customer_request)
        assert response.status_code == 200
        data = response.json()
        assert "churn_probability" in data
        assert "risk_level" in data
    
    def test_get_segments(self):
        """Test get segments endpoint."""
        response = client.get("/api/v1/customer/segments")
        assert response.status_code == 200
        data = response.json()
        assert "segments" in data
        assert len(data["segments"]) > 0
    
    def test_customer_health(self):
        """Test customer service health."""
        response = client.get("/api/v1/customer/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestCompetitorEndpoints:
    """Test competitor analysis endpoints."""
    
    @pytest.fixture
    def valid_competitor_request(self):
        """Valid competitor request fixture."""
        return {
            "product_id": "PROD001",
            "your_current_price": 1000,
            "competitor_prices": {
                "CompetitorA": 950,
                "CompetitorB": 980,
                "CompetitorC": 1020
            }
        }
    
    def test_analyze_competitors(self, valid_competitor_request):
        """Test competitor analysis endpoint."""
        response = client.post("/api/v1/competitor/analyze", json=valid_competitor_request)
        assert response.status_code == 200
        data = response.json()
        assert "average_competitor_price" in data
        assert "your_price_position" in data
        assert "price_difference_percent" in data
        assert "market_share_potential" in data
    
    def test_track_competitor_prices(self):
        """Test competitor price tracking."""
        response = client.post(
            "/api/v1/competitor/track",
            params={
                "product_id": "PROD001",
                "competitor_prices": {
                    "CompetitorA": 950,
                    "CompetitorB": 980
                }
            }
        )
        assert response.status_code == 200
    
    def test_competitor_health(self):
        """Test competitor service health."""
        response = client.get("/api/v1/competitor/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestErrorHandling:
    """Test error handling."""
    
    def test_invalid_pricing_request(self):
        """Test invalid pricing request."""
        response = client.post(
            "/api/v1/pricing/predict",
            json={
                "current_price": -100,  # Invalid negative price
                "competitor_price": 950,
                "demand": 200,
                "inventory": 50,
                "conversion_rate": 0.12,
                "promotion": 1,
                "discount_percent": 10,
                "demand_index": 0.75
            }
        )
        assert response.status_code == 422  # Validation error
    
    def test_forecast_insufficient_data(self):
        """Test forecast with insufficient data."""
        response = client.post(
            "/api/v1/forecast/demand",
            json={
                "product_id": "PROD001",
                "historical_demand": [100],  # Only 1 data point
                "days_ahead": 30
            }
        )
        assert response.status_code == 400  # Bad request


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
