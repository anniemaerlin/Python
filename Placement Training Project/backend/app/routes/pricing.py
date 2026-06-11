"""
Pricing routes module.
Endpoints for dynamic pricing predictions and revenue simulations.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
import logging
from typing import Optional
from app.schemas.pricing_schema import (
    PricingPredictionRequest,
    PricingPredictionResponse,
    PricingExplanationResponse,
    RevenueSimulationRequest,
    RevenueSimulationResponse
)
from app.services.pricing_service import PricingService
from app.database.firebase import FirebaseDB

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/pricing", tags=["Pricing"])


@router.post(
    "/predict",
    response_model=PricingPredictionResponse,
    summary="Predict Optimal Price",
    description="Get AI-recommended optimal price for a product based on market conditions"
)
async def predict_price(
    request: PricingPredictionRequest,
    model: str = Query("xgboost", description="ML model to use: xgboost or random_forest")
):
    """
    Predict the optimal price for a product using machine learning.
    
    - **current_price**: Product's current price
    - **competitor_price**: Competitor's price for similar product
    - **demand**: Current customer demand
    - **inventory**: Available inventory units
    - **conversion_rate**: Current conversion rate (0-1)
    - **promotion**: Is promotion active (0 or 1)
    - **discount_percent**: Current discount percentage
    - **demand_index**: Demand index (0-1)
    
    Returns recommended price with confidence score.
    """
    try:
        logger.info(f"Price prediction request received with model: {model}")
        
        # Validate model choice
        if model not in ["xgboost", "random_forest"]:
            raise HTTPException(status_code=400, detail="Model must be 'xgboost' or 'random_forest'")
        
        # Get prediction
        prediction = PricingService.predict_price(request.dict(), model)
        
        # Save to database
        FirebaseDB.save_pricing_prediction(
            product_id=f"pred_{prediction['timestamp']}",
            prediction_data=prediction
        )
        
        logger.info(f"Price prediction completed: {prediction['recommended_price']}")
        return prediction
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in price prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/predict-with-explanation",
    response_model=PricingExplanationResponse,
    summary="Predict Price with Explanation",
    description="Get AI-recommended price with feature importance and human-readable explanation"
)
async def predict_price_with_explanation(
    request: PricingPredictionRequest,
    model: str = Query("xgboost", description="ML model to use: xgboost or random_forest")
):
    """
    Predict optimal price with explainable AI features.
    
    Returns:
    - Recommended price
    - Model used
    - Confidence score
    - Feature importance scores
    - Top factors influencing the price
    - Human-readable explanation
    """
    try:
        logger.info(f"Price prediction with explanation requested using model: {model}")
        
        if model not in ["xgboost", "random_forest"]:
            raise HTTPException(status_code=400, detail="Model must be 'xgboost' or 'random_forest'")
        
        # Get prediction with explanation
        prediction = PricingService.predict_price_with_explanation(request.dict(), model)
        
        # Save to database
        FirebaseDB.save_pricing_prediction(
            product_id=f"pred_exp_{prediction['timestamp']}",
            prediction_data=prediction
        )
        
        logger.info("Price prediction with explanation completed")
        return prediction
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in price prediction with explanation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/simulate-revenue",
    response_model=RevenueSimulationResponse,
    summary="Simulate Revenue Impact",
    description="Simulate revenue impact of price changes"
)
async def simulate_revenue_impact(request: RevenueSimulationRequest):
    """
    Simulate the revenue impact of changing the price.
    
    Uses price elasticity of demand to estimate:
    - New demand at proposed price
    - Projected revenue
    - Revenue change percentage
    
    Helps in making informed pricing decisions.
    """
    try:
        logger.info("Revenue simulation requested")
        
        # Validate inputs
        if request.current_price <= 0:
            raise HTTPException(status_code=400, detail="Current price must be positive")
        if request.proposed_price <= 0:
            raise HTTPException(status_code=400, detail="Proposed price must be positive")
        if request.current_demand < 0:
            raise HTTPException(status_code=400, detail="Current demand cannot be negative")
        
        # Simulate revenue
        simulation = PricingService.simulate_revenue_impact(
            current_price=request.current_price,
            current_demand=request.current_demand,
            proposed_price=request.proposed_price,
            price_elasticity=request.price_elasticity
        )
        
        # Save to database
        FirebaseDB.save_pricing_prediction(
            product_id=f"sim_{simulation['timestamp']}",
            prediction_data=simulation
        )
        
        logger.info("Revenue simulation completed")
        return simulation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in revenue simulation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/health",
    summary="Check Pricing Service Health",
    description="Check if pricing service and models are operational"
)
async def pricing_health():
    """
    Health check endpoint for pricing service.
    """
    try:
        models_loaded = PricingService.are_models_loaded()
        
        health_status = {
            "status": "healthy" if models_loaded else "degraded",
            "models_loaded": models_loaded,
            "service": "pricing",
            "timestamp": None
        }
        
        logger.info(f"Health check: {health_status}")
        return health_status
        
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")
