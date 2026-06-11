"""
Demand forecasting routes module.
Endpoints for demand prediction and inventory recommendations.
"""

from fastapi import APIRouter, HTTPException, Query, Body
import logging
from typing import List, Optional, Dict, Any
from app.schemas.pricing_schema import (
    DemandForecastRequest,
    DemandForecastResponse
)
from app.services.forecast_service import ForecastService
from app.database.firebase import FirebaseDB

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/forecast", tags=["Demand Forecasting"])


@router.post(
    "/demand",
    response_model=DemandForecastResponse,
    summary="Forecast Demand",
    description="Predict future customer demand using time series analysis"
)
async def forecast_demand(
    request: DemandForecastRequest,
    seasonality: str = Query("none", description="Seasonality pattern: none, weekly, monthly")
):
    """
    Forecast future demand for a product.
    
    - **product_id**: Product identifier
    - **historical_demand**: Historical demand data points
    - **days_ahead**: Number of days to forecast (1-365)
    - **seasonality**: Seasonality pattern (none, weekly, monthly)
    
    Returns forecast with confidence intervals and trend analysis.
    """
    try:
        logger.info(f"Demand forecast requested for product {request.product_id}")
        
        # Validate inputs
        if not request.historical_demand or len(request.historical_demand) < 3:
            raise HTTPException(
                status_code=400,
                detail="Need at least 3 historical data points"
            )
        
        if request.days_ahead < 1 or request.days_ahead > 365:
            raise HTTPException(
                status_code=400,
                detail="Days ahead must be between 1 and 365"
            )
        
        # Generate forecast
        forecast = ForecastService.forecast_demand(
            historical_demand=request.historical_demand,
            days_ahead=request.days_ahead,
            seasonality=seasonality
        )
        
        # Add product ID
        forecast['product_id'] = request.product_id
        
        # Save to database
        FirebaseDB.save_demand_forecast(
            product_id=request.product_id,
            forecast_data=forecast
        )
        
        logger.info(f"Demand forecast completed for product {request.product_id}")
        return forecast
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error forecasting demand: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/insights",
    summary="Get Demand Insights",
    description="Analyze historical demand data to generate insights"
)
async def get_demand_insights(
    product_id: str = Query(..., description="Product identifier"),
    historical_demand: List[float] = Query(..., description="Historical demand data points")
):
    """
    Generate insights from historical demand data.
    
    Returns:
    - Average demand
    - Peak and minimum demand
    - Demand volatility
    - Demand variance
    - Coefficient of variation
    """
    try:
        logger.info(f"Demand insights requested for product {product_id}")
        
        if not historical_demand or len(historical_demand) < 2:
            raise HTTPException(
                status_code=400,
                detail="Need at least 2 historical data points"
            )
        
        # Calculate insights
        insights = ForecastService.get_demand_insights(historical_demand)
        insights['product_id'] = product_id
        
        logger.info(f"Demand insights calculated for product {product_id}")
        return insights
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating demand insights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/inventory-recommendation",
    summary="Get Inventory Recommendations",
    description="Recommend inventory levels based on demand forecast"
)
async def get_inventory_recommendations(
    data: Dict[str, Any] = Body(
        ...,
        example={
            "product_id": "PROD-001",
            "historical_demand": [50, 55, 60, 65, 70],
            "current_inventory": 150,
            "lead_time_days": 7
        }
    )
):
    """
    Get inventory level recommendations based on demand forecast.
    Accepts POST body with product_id, historical_demand, current_inventory, lead_time_days.
    """
    try:
        product_id = data.get("product_id", "unknown")
        historical_demand = data.get("historical_demand", [])
        current_inventory = data.get("current_inventory", 0)
        lead_time_days    = data.get("lead_time_days", 7)
        safety_stock_mult = data.get("safety_stock_multiplier", 1.5)

        logger.info(f"Inventory recommendations requested for product {product_id}")

        if not historical_demand or len(historical_demand) < 2:
            raise HTTPException(
                status_code=400,
                detail="Need at least 2 historical demand data points"
            )

        import numpy as np
        demand_arr = np.array(historical_demand, dtype=float)
        avg_daily  = float(demand_arr.mean())
        peak       = float(demand_arr.max())
        safety     = float(avg_daily * safety_stock_mult)
        reorder_pt = float(avg_daily * lead_time_days + safety)
        order_qty  = float(reorder_pt * 2)
        days_supply = float(current_inventory / avg_daily) if avg_daily > 0 else 999

        recommendations = {
            "product_id":                 product_id,
            "average_daily_demand":       round(avg_daily, 1),
            "peak_demand":                round(peak, 1),
            "safety_stock":               round(safety, 0),
            "reorder_point":              round(reorder_pt, 0),
            "recommended_order_quantity": round(order_qty, 0),
            "days_of_supply":             round(days_supply, 1),
            "current_inventory":          current_inventory,
            "is_understocked":            current_inventory < reorder_pt
        }

        logger.info(f"Inventory recommendations generated for product {product_id}")
        return recommendations

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating inventory recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/health",
    summary="Check Forecast Service Health",
    description="Check if forecasting service is operational"
)
async def forecast_health():
    """
    Health check endpoint for forecast service.
    """
    try:
        health_status = {
            "status": "healthy",
            "service": "forecast",
            "timestamp": None
        }
        
        logger.info(f"Health check: {health_status}")
        return health_status
        
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")
