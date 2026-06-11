"""
Pydantic schemas for pricing API requests and responses.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from enum import Enum


class DemandTrendEnum(str, Enum):
    """Enum for demand trends."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PricingPredictionRequest(BaseModel):
    """Request schema for dynamic price prediction."""
    
    current_price: float = Field(..., gt=0, description="Current product price")
    competitor_price: float = Field(..., gt=0, description="Competitor's product price")
    demand: int = Field(..., ge=0, description="Current demand count")
    inventory: int = Field(..., ge=0, description="Available inventory units")
    conversion_rate: float = Field(..., ge=0, le=1, description="Current conversion rate (0-1)")
    promotion: int = Field(default=0, ge=0, le=1, description="Is promotion active (0 or 1)")
    discount_percent: float = Field(default=0, ge=0, le=100, description="Discount percentage")
    demand_index: float = Field(..., ge=0, le=1, description="Demand index (0-1)")
    
    class Config:
        schema_extra = {
            "example": {
                "current_price": 1000,
                "competitor_price": 950,
                "demand": 200,
                "inventory": 50,
                "conversion_rate": 0.12,
                "promotion": 1,
                "discount_percent": 10,
                "demand_index": 0.75
            }
        }


class PricingPredictionResponse(BaseModel):
    """Response schema for dynamic price prediction."""
    
    recommended_price: float = Field(..., description="Recommended optimal price")
    model_used: str = Field(..., description="ML model used for prediction")
    confidence_score: float = Field(..., ge=0, le=100, description="Confidence score of prediction")
    price_change_percent: float = Field(default=0, description="Percentage change from current price")
    revenue_impact: float = Field(default=0, description="Estimated revenue impact")
    
    class Config:
        schema_extra = {
            "example": {
                "recommended_price": 1080,
                "model_used": "XGBoost",
                "confidence_score": 94,
                "price_change_percent": 8.0,
                "revenue_impact": 1500.50
            }
        }


class PricingExplanationResponse(BaseModel):
    """Response schema for explainable pricing prediction."""
    
    recommended_price: float
    model_used: str
    confidence_score: float
    feature_importance: Dict[str, float] = Field(..., description="Feature importance scores")
    top_factors: list = Field(..., description="Top factors influencing the price")
    explanation: str = Field(..., description="Human-readable explanation of the prediction")
    
    class Config:
        schema_extra = {
            "example": {
                "recommended_price": 1080,
                "model_used": "XGBoost",
                "confidence_score": 94,
                "feature_importance": {
                    "demand": 0.35,
                    "competitor_price": 0.25,
                    "inventory": 0.20,
                    "conversion_rate": 0.12,
                    "promotion": 0.08
                },
                "top_factors": [
                    "High demand detected (200 units)",
                    "Low inventory (50 units)",
                    "Competitor price is lower (950 vs 1000)"
                ],
                "explanation": "Price increased by 8% due to high demand and low inventory"
            }
        }


class DemandForecastRequest(BaseModel):
    """Request schema for demand forecasting."""
    
    product_id: str = Field(..., description="Product identifier")
    historical_demand: list = Field(..., min_items=1, description="Historical demand data")
    days_ahead: int = Field(default=30, ge=1, le=365, description="Days to forecast ahead")
    seasonality: Optional[str] = Field(default="none", description="Seasonality pattern")
    
    class Config:
        schema_extra = {
            "example": {
                "product_id": "PROD001",
                "historical_demand": [100, 110, 120, 115, 130, 125, 140],
                "days_ahead": 30,
                "seasonality": "weekly"
            }
        }


class DemandForecastResponse(BaseModel):
    """Response schema for demand forecast."""
    
    product_id: str
    forecasted_demand: list = Field(..., description="Forecasted demand for next period")
    trend: DemandTrendEnum = Field(..., description="Demand trend direction")
    confidence_interval_lower: list = Field(..., description="Lower bound of confidence interval")
    confidence_interval_upper: list = Field(..., description="Upper bound of confidence interval")
    prediction_accuracy: float = Field(..., ge=0, le=100, description="Accuracy of the model")
    
    class Config:
        schema_extra = {
            "example": {
                "product_id": "PROD001",
                "forecasted_demand": [145, 150, 155, 160, 158],
                "trend": "high",
                "confidence_interval_lower": [140, 145, 150, 155, 153],
                "confidence_interval_upper": [150, 155, 160, 165, 163],
                "prediction_accuracy": 92.5
            }
        }


class CompetitorAnalysisRequest(BaseModel):
    """Request schema for competitor price analysis."""
    
    product_id: str = Field(..., description="Product identifier")
    your_current_price: float = Field(..., gt=0, description="Your current price")
    competitor_prices: Dict[str, float] = Field(..., description="Competitor names and prices")
    
    class Config:
        schema_extra = {
            "example": {
                "product_id": "PROD001",
                "your_current_price": 1000,
                "competitor_prices": {
                    "CompetitorA": 950,
                    "CompetitorB": 980,
                    "CompetitorC": 1020
                }
            }
        }


class CompetitorAnalysisResponse(BaseModel):
    """Response schema for competitor analysis."""
    
    product_id: str
    average_competitor_price: float
    your_price_position: str = Field(..., description="Position relative to competitors (above/at/below)")
    price_difference_percent: float = Field(..., description="Percentage difference from average")
    recommended_action: str = Field(..., description="Recommended pricing action")
    market_share_potential: float = Field(..., ge=0, le=100, description="Potential market share impact")
    
    class Config:
        schema_extra = {
            "example": {
                "product_id": "PROD001",
                "average_competitor_price": 983.33,
                "your_price_position": "above",
                "price_difference_percent": 1.69,
                "recommended_action": "Consider slight price reduction to increase competitiveness",
                "market_share_potential": 75.5
            }
        }


class CustomerSegmentRequest(BaseModel):
    """Request schema for customer segmentation."""
    
    customer_data: Dict[str, Any] = Field(..., description="Customer profile data")
    
    class Config:
        schema_extra = {
            "example": {
                "customer_data": {
                    "purchase_frequency": 12,
                    "average_order_value": 500,
                    "customer_lifetime_value": 6000,
                    "loyalty_score": 0.85
                }
            }
        }


class CustomerSegmentResponse(BaseModel):
    """Response schema for customer segmentation."""
    
    segment: str = Field(..., description="Customer segment classification")
    segment_description: str = Field(..., description="Description of the segment")
    recommended_price_elasticity: float = Field(..., description="Price elasticity for this segment")
    recommended_discount: float = Field(..., ge=0, le=100, description="Recommended discount percentage")
    retention_probability: float = Field(..., ge=0, le=1, description="Customer retention probability")


class RevenueSimulationRequest(BaseModel):
    """Request schema for revenue impact simulation."""
    
    current_price: float = Field(..., gt=0, description="Current price")
    current_demand: int = Field(..., ge=0, description="Current demand")
    proposed_price: float = Field(..., gt=0, description="Proposed new price")
    price_elasticity: float = Field(..., description="Price elasticity of demand")
    
    class Config:
        schema_extra = {
            "example": {
                "current_price": 1000,
                "current_demand": 100,
                "proposed_price": 1100,
                "price_elasticity": -1.5
            }
        }


class RevenueSimulationResponse(BaseModel):
    """Response schema for revenue simulation."""
    
    current_revenue: float = Field(..., description="Current revenue at existing price")
    projected_revenue: float = Field(..., description="Projected revenue at proposed price")
    revenue_change_percent: float = Field(..., description="Percentage change in revenue")
    projected_demand: int = Field(..., description="Projected demand at new price")
    recommendation: str = Field(..., description="Pricing recommendation based on simulation")


class HealthCheckResponse(BaseModel):
    """Response schema for health check."""
    
    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")
    models_loaded: bool = Field(..., description="Whether ML models are loaded")


class ErrorResponse(BaseModel):
    """Response schema for error responses."""
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    request_id: Optional[str] = Field(None, description="Request ID for tracing")
