# API Testing Guide

## Overview

This guide covers testing the Dynamic Pricing Engine API comprehensively using various tools and methods.

## Table of Contents
1. [Using Swagger UI](#using-swagger-ui)
2. [Using cURL](#using-curl)
3. [Using Postman](#using-postman)
4. [Using Python Requests](#using-python-requests)
5. [Running Test Suite](#running-test-suite)
6. [Load Testing](#load-testing)

---

## Using Swagger UI

**URL:** http://localhost:8000/api/docs

### Steps:
1. Open the Swagger UI URL
2. Find the endpoint you want to test
3. Click "Try it out"
4. Fill in parameters/request body
5. Click "Execute"
6. View the response

---

## Using cURL

### 1. Health Check
```bash
curl http://localhost:8000/api/health
```

### 2. Price Prediction
```bash
curl -X POST "http://localhost:8000/api/v1/pricing/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "current_price": 1000,
    "competitor_price": 950,
    "demand": 200,
    "inventory": 50,
    "conversion_rate": 0.12,
    "promotion": 1,
    "discount_percent": 10,
    "demand_index": 0.75
  }'
```

### 3. Price Prediction with Explanation
```bash
curl -X POST "http://localhost:8000/api/v1/pricing/predict-with-explanation" \
  -H "Content-Type: application/json" \
  -d '{
    "current_price": 1000,
    "competitor_price": 950,
    "demand": 200,
    "inventory": 50,
    "conversion_rate": 0.12,
    "promotion": 1,
    "discount_percent": 10,
    "demand_index": 0.75
  }'
```

### 4. Revenue Simulation
```bash
curl -X POST "http://localhost:8000/api/v1/pricing/simulate-revenue" \
  -H "Content-Type: application/json" \
  -d '{
    "current_price": 1000,
    "current_demand": 100,
    "proposed_price": 1100,
    "price_elasticity": -1.5
  }'
```

### 5. Demand Forecast
```bash
curl -X POST "http://localhost:8000/api/v1/forecast/demand" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "PROD001",
    "historical_demand": [100, 110, 120, 115, 130, 125, 140],
    "days_ahead": 30,
    "seasonality": "weekly"
  }'
```

### 6. Demand Insights
```bash
curl -X POST "http://localhost:8000/api/v1/forecast/insights" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "PROD001",
    "historical_demand": [100, 110, 120, 115, 130, 125, 140]
  }'
```

### 7. Inventory Recommendations
```bash
curl -X POST "http://localhost:8000/api/v1/forecast/inventory-recommendation" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "PROD001",
    "forecasted_demand": [100, 110, 120, 115, 130, 125, 140]
  }'
```

### 8. Customer Segmentation
```bash
curl -X POST "http://localhost:8000/api/v1/customer/segment" \
  -H "Content-Type: application/json" \
  -d '{
    "purchase_frequency": 12,
    "average_order_value": 500,
    "customer_lifetime_value": 6000,
    "loyalty_score": 0.85
  }'
```

### 9. Churn Prediction
```bash
curl -X POST "http://localhost:8000/api/v1/customer/churn-prediction" \
  -H "Content-Type: application/json" \
  -d '{
    "purchase_frequency": 5,
    "average_order_value": 250,
    "customer_lifetime_value": 2000,
    "loyalty_score": 0.4,
    "days_since_purchase": 120
  }'
```

### 10. Competitor Analysis
```bash
curl -X POST "http://localhost:8000/api/v1/competitor/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "PROD001",
    "your_current_price": 1000,
    "competitor_prices": {
      "CompetitorA": 950,
      "CompetitorB": 980,
      "CompetitorC": 1020
    }
  }'
```

---

## Using Postman

### Setup:
1. Download and install Postman
2. Import collection from: http://localhost:8000/api/openapi.json

### Or Create Requests Manually:

1. **Create New Request**
2. **Set Method:** POST/GET
3. **Set URL:** http://localhost:8000/api/v1/...
4. **Go to Body Tab:** Select "raw" and "JSON"
5. **Paste request payload**
6. **Click Send**

---

## Using Python Requests

### Run Example Script:
```bash
python example_usage.py
```

### Create Custom Test Script:
```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Test price prediction
response = requests.post(
    f"{BASE_URL}/pricing/predict",
    json={
        "current_price": 1000,
        "competitor_price": 950,
        "demand": 200,
        "inventory": 50,
        "conversion_rate": 0.12,
        "promotion": 1,
        "discount_percent": 10,
        "demand_index": 0.75
    }
)

print("Status Code:", response.status_code)
print("Response:", json.dumps(response.json(), indent=2))
```

---

## Running Test Suite

### Prerequisites:
```bash
pip install pytest pytest-asyncio httpx
```

### Run All Tests:
```bash
pytest tests/
```

### Run Specific Test:
```bash
pytest tests/test_endpoints.py::TestPricingEndpoints::test_predict_price -v
```

### Run with Coverage:
```bash
pip install pytest-cov
pytest tests/ --cov=app
```

### Example Test Output:
```
tests/test_endpoints.py::TestHealthEndpoints::test_root_endpoint PASSED    [10%]
tests/test_endpoints.py::TestHealthEndpoints::test_health_check PASSED     [20%]
tests/test_endpoints.py::TestPricingEndpoints::test_predict_price PASSED   [30%]
...
```

---

## Load Testing

### Using Apache Bench:
```bash
# Install: apt-get install apache2-utils

# Run 1000 requests with 10 concurrent:
ab -n 1000 -c 10 http://localhost:8000/api/health
```

### Using Locust:
```bash
# Install
pip install locust

# Create locustfile.py (example below)

# Run load test
locust -f locustfile.py --host=http://localhost:8000
```

### Example locustfile.py:
```python
from locust import HttpUser, task, between
import json

class PricingUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def predict_price(self):
        payload = {
            "current_price": 1000,
            "competitor_price": 950,
            "demand": 200,
            "inventory": 50,
            "conversion_rate": 0.12,
            "promotion": 1,
            "discount_percent": 10,
            "demand_index": 0.75
        }
        self.client.post("/api/v1/pricing/predict", json=payload)
    
    @task
    def forecast_demand(self):
        payload = {
            "product_id": "PROD001",
            "historical_demand": [100, 110, 120, 115, 130, 125, 140],
            "days_ahead": 30
        }
        self.client.post("/api/v1/forecast/demand", json=payload)
    
    @task
    def health_check(self):
        self.client.get("/api/health")
```

### Using ab Results Interpretation:
```
Requests per second:    50.25 [#/sec]
Time per request:       19.90 [ms]
Failed requests:        0
```

---

## Test Scenarios

### Scenario 1: Normal Operations
```bash
# 1. Check health
curl http://localhost:8000/api/health

# 2. Make price prediction
curl -X POST http://localhost:8000/api/v1/pricing/predict \
  -H "Content-Type: application/json" \
  -d '{"current_price": 1000, "competitor_price": 950, ...}'

# 3. Check results
# Should receive 200 status with recommended price
```

### Scenario 2: Input Validation
```bash
# Test with invalid data
curl -X POST http://localhost:8000/api/v1/pricing/predict \
  -H "Content-Type: application/json" \
  -d '{"current_price": -100, ...}'

# Should receive 422 status (validation error)
```

### Scenario 3: Error Handling
```bash
# Test with missing required field
curl -X POST http://localhost:8000/api/v1/pricing/predict \
  -H "Content-Type: application/json" \
  -d '{"current_price": 1000}'

# Should receive 422 status with error details
```

---

## Performance Benchmarks

Expected response times:
- Health Check: < 10ms
- Price Prediction: 50-100ms
- Demand Forecast: 30-50ms
- Customer Segmentation: 20-30ms
- Competitor Analysis: 30-50ms

---

## Troubleshooting

### Issue: Connection refused
- **Solution:** Ensure API is running: `python -m uvicorn app.main:app --reload`

### Issue: Invalid JSON error
- **Solution:** Ensure JSON is properly formatted, use -d '@file.json' for complex payloads

### Issue: Timeout
- **Solution:** API might be busy, check logs or increase timeout

### Issue: 422 Validation Error
- **Solution:** Check required fields and data types match schema

---

## Additional Resources

- [API Documentation](http://localhost:8000/api/docs)
- [README.md](README.md)
- [QUICKSTART.md](QUICKSTART.md)
- [example_usage.py](example_usage.py)

