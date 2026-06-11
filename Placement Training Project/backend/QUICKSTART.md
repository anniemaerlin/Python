# Quick Start Guide - Dynamic Pricing Engine Backend

## Installation & Setup (5 minutes)

### 1. Install Dependencies
```bash
# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env if needed (default settings usually work fine)
```

### 3. Run the Server
```bash
# Windows
run.bat

# macOS/Linux
bash run.sh

# Or directly
python -m uvicorn app.main:app --reload
```

The server will start at: **http://localhost:8000**

## API Documentation

### View API Docs
- **Interactive Docs**: http://localhost:8000/api/docs
- **Alternative Docs**: http://localhost:8000/api/redoc

### Quick Test Examples

#### 1. Test Price Prediction
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

#### 2. Test Health Check
```bash
curl http://localhost:8000/api/health
```

#### 3. Test Demand Forecast
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

#### 4. Test Customer Segmentation
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

#### 5. Test Competitor Analysis
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

## Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

## Project Structure Overview

```
backend/
├── app/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration
│   ├── routes/                 # API endpoints
│   │   ├── pricing.py          # Price prediction APIs
│   │   ├── forecast.py         # Forecasting APIs
│   │   ├── customer.py         # Customer APIs
│   │   └── competitor.py       # Competitor APIs
│   ├── services/               # Business logic
│   │   ├── pricing_service.py  # ML predictions
│   │   ├── forecast_service.py # Forecasting logic
│   │   └── segmentation_service.py
│   ├── database/               # Data layer
│   │   └── firebase.py         # Firestore integration
│   ├── schemas/                # Data models
│   │   └── pricing_schema.py   # Pydantic schemas
│   └── models/                 # ML models
├── tests/                      # Test files
├── requirements.txt            # Dependencies
├── .env.example               # Environment template
├── run.sh & run.bat          # Start scripts
└── README.md                  # Full documentation
```

## Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Welcome page |
| `/api/health` | GET | Health check |
| `/api/v1/pricing/predict` | POST | Get optimal price |
| `/api/v1/pricing/predict-with-explanation` | POST | Price with explanations |
| `/api/v1/pricing/simulate-revenue` | POST | Revenue simulation |
| `/api/v1/forecast/demand` | POST | Demand forecast |
| `/api/v1/forecast/insights` | POST | Demand insights |
| `/api/v1/customer/segment` | POST | Customer segmentation |
| `/api/v1/customer/churn-prediction` | POST | Churn prediction |
| `/api/v1/competitor/analyze` | POST | Competitor analysis |

## Troubleshooting

**Problem**: Models not loading
- **Solution**: Models are auto-created on first run. Check `logs/app.log`

**Problem**: Port 8000 already in use
- **Solution**: Change `API_PORT` in `.env` or run: `python -m uvicorn app.main:app --port 8001`

**Problem**: Import errors
- **Solution**: Ensure virtual environment is activated and `pip install -r requirements.txt` is run

**Problem**: Firebase not connecting
- **Solution**: Firebase is optional. Set `ENABLE_FIREBASE=false` in `.env` to skip

## Next Steps

1. ✅ Server is running
2. 📖 Read full [README.md](README.md)
3. 🧪 Run tests: `pytest tests/`
4. 🔌 Connect your frontend to the APIs
5. 🚀 Deploy to production

## Support

- 📚 API Docs: http://localhost:8000/api/docs
- 📖 README: See README.md
- 🐛 Issues: Check logs/app.log

Enjoy using the Dynamic Pricing Engine!
