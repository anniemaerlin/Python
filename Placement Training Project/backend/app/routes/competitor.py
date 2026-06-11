"""
Competitor analysis routes module.
Endpoints for competitor price tracking and analysis.
"""

from fastapi import APIRouter, HTTPException, Body, Query
import logging
from typing import Dict, Any, List
from statistics import mean, stdev
from app.schemas.pricing_schema import (
    CompetitorAnalysisRequest,
    CompetitorAnalysisResponse
)
from app.database.firebase import FirebaseDB

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/competitor", tags=["Competitor Analysis"])


@router.post(
    "/analyze",
    response_model=CompetitorAnalysisResponse,
    summary="Analyze Competitor Prices",
    description="Analyze competitive positioning and get pricing recommendations"
)
async def analyze_competitors(request: CompetitorAnalysisRequest):
    """
    Analyze competitor prices and recommend pricing strategy.
    
    - **product_id**: Product identifier
    - **your_current_price**: Your current price
    - **competitor_prices**: Dictionary of competitor names and prices
    
    Returns:
    - Average competitor price
    - Your price position (above/at/below)
    - Price difference percentage
    - Recommended pricing action
    - Market share potential
    """
    try:
        logger.info(f"Competitor analysis requested for product {request.product_id}")
        
        # Validate inputs
        if not request.competitor_prices or len(request.competitor_prices) == 0:
            raise HTTPException(
                status_code=400,
                detail="At least one competitor price is required"
            )
        
        for comp_name, price in request.competitor_prices.items():
            if price <= 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Competitor price for {comp_name} must be positive"
                )
        
        # Calculate statistics
        competitor_prices = list(request.competitor_prices.values())
        avg_competitor_price = mean(competitor_prices)
        
        # Determine your position
        if request.your_current_price > avg_competitor_price:
            position = "above"
        elif request.your_current_price < avg_competitor_price:
            position = "below"
        else:
            position = "at"
        
        # Calculate price difference percentage
        price_difference_percent = (
            (request.your_current_price - avg_competitor_price) / avg_competitor_price * 100
        )
        
        # Generate recommendation
        recommendation = _generate_competitor_recommendation(
            position=position,
            price_difference_percent=price_difference_percent,
            your_price=request.your_current_price,
            avg_price=avg_competitor_price
        )
        
        # Estimate market share potential
        market_share = _estimate_market_share(
            position=position,
            price_difference_percent=price_difference_percent
        )
        
        result = {
            "product_id": request.product_id,
            "average_competitor_price": round(avg_competitor_price, 2),
            "your_price_position": position,
            "price_position": position,  # alias for frontend compatibility
            "price_difference_percent": round(price_difference_percent, 2),
            "recommended_action": recommendation,
            "market_share_potential": round(market_share, 2)
        }
        
        # Add detailed competitor breakdown
        result["competitor_breakdown"] = {
            name: {"price": price, "difference": round(price - request.your_current_price, 2)}
            for name, price in request.competitor_prices.items()
        }
        
        # Save to database
        FirebaseDB.save_competitor_analysis(
            product_id=request.product_id,
            analysis_data=result
        )
        
        logger.info(f"Competitor analysis completed for product {request.product_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing competitors: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/track",
    summary="Track Competitor Prices",
    description="Track and store competitor price changes over time"
)
async def track_competitor_prices(
    product_id: str = Query(..., description="Product identifier"),
    competitor_prices: Dict[str, float] = Body(..., description="Current competitor prices")
):
    """
    Track competitor prices for historical analysis.
    
    This endpoint stores competitor prices for trend analysis and pattern detection.
    """
    try:
        logger.info(f"Competitor price tracking requested for product {product_id}")
        
        # Validate inputs
        if not competitor_prices or len(competitor_prices) == 0:
            raise HTTPException(
                status_code=400,
                detail="At least one competitor price is required"
            )
        
        # Store tracking data
        tracking_data = {
            "product_id": product_id,
            "competitor_prices": competitor_prices,
            "price_count": len(competitor_prices),
            "average_price": round(mean(competitor_prices.values()), 2),
            "min_price": round(min(competitor_prices.values()), 2),
            "max_price": round(max(competitor_prices.values()), 2)
        }
        
        if len(competitor_prices.values()) > 1:
            tracking_data["price_std_dev"] = round(stdev(competitor_prices.values()), 2)
        
        # Save tracking data
        FirebaseDB.save_analytics_event(
            event_name="competitor_price_tracked",
            event_data=tracking_data
        )
        
        logger.info(f"Competitor prices tracked for product {product_id}")
        return tracking_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error tracking competitor prices: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/pricing-strategy",
    summary="Get Competitive Pricing Strategy",
    description="Get recommended pricing strategy based on competitive analysis"
)
async def get_pricing_strategy(
    request: CompetitorAnalysisRequest,
    your_margin_percent: float = Query(default=20, description="Your margin percentage")
):
    """
    Get recommended competitive pricing strategy.
    """
    try:
        product_id         = request.product_id
        your_current_price = request.your_current_price
        competitor_prices_dict = request.competitor_prices

        logger.info(f"Pricing strategy requested for product {product_id}")

        if not competitor_prices_dict:
            raise HTTPException(status_code=400, detail="Competitor prices required")

        if your_margin_percent < 0 or your_margin_percent > 100:
            raise HTTPException(status_code=400, detail="Margin must be between 0-100%")
        
        # Calculate pricing strategy
        competitor_prices_list = list(competitor_prices_dict.values())
        avg_price = mean(competitor_prices_list)
        min_price = min(competitor_prices_list)
        max_price = max(competitor_prices_list)
        
        # Calculate your cost (reverse from margin)
        your_cost = your_current_price / (1 + your_margin_percent / 100)
        
        # Recommended price range
        min_recommended = your_cost * (1 + your_margin_percent / 100)
        max_recommended = max_price
        optimal_price = mean([min_recommended, avg_price])
        
        strategy = {
            "product_id": product_id,
            "strategy": _get_strategy_recommendation(your_current_price, avg_price, optimal_price),
            "suggested_price": round(optimal_price, 2),
            "rationale": f"Based on {len(competitor_prices_dict)} competitors. Market avg ₹{avg_price:.0f}, optimal price ₹{optimal_price:.0f}.",
            "market_analysis": {
                "average_competitor_price": round(avg_price, 2),
                "lowest_competitor_price": round(min_price, 2),
                "highest_competitor_price": round(max_price, 2),
                "price_range": round(max_price - min_price, 2),
                "competitor_count": len(competitor_prices_dict)
            },
            "cost_analysis": {
                "estimated_cost": round(your_cost, 2),
                "current_margin_percent": your_margin_percent,
                "current_price": your_current_price
            },
            "recommendations": {
                "minimum_price": round(min_recommended, 2),
                "optimal_price": round(optimal_price, 2),
                "maximum_price": round(max_recommended, 2),
            },
            "competitive_positioning": _get_competitive_positioning(
                your_current_price, min_price, avg_price, max_price
            )
        }
        
        logger.info(f"Pricing strategy generated for product {product_id}")
        return strategy
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting pricing strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def _generate_competitor_recommendation(position: str, price_difference_percent: float,
                                       your_price: float, avg_price: float) -> str:
    """Generate pricing recommendation based on competitor analysis."""
    if position == "above":
        if price_difference_percent > 10:
            return f"Your price is {abs(price_difference_percent):.1f}% above competitors. Consider price reduction to ${avg_price:.2f} to increase competitiveness"
        else:
            return "Your price is competitive. Monitor competitor moves closely"
    elif position == "below":
        if price_difference_percent < -10:
            return f"Your price is {abs(price_difference_percent):.1f}% below competitors. Consider increasing to ${avg_price:.2f} to improve margins"
        else:
            return "Your price is competitive and offers good value"
    else:
        return "Your price is aligned with market average. Monitor for changes"


def _estimate_market_share(position: str, price_difference_percent: float) -> float:
    """Estimate potential market share based on pricing position."""
    base_share = 20.0
    
    if position == "below":
        if price_difference_percent < -15:
            return base_share + 25
        elif price_difference_percent < -10:
            return base_share + 15
        else:
            return base_share + 5
    elif position == "above":
        if price_difference_percent > 15:
            return base_share - 15
        elif price_difference_percent > 10:
            return base_share - 8
        else:
            return base_share - 2
    else:
        return base_share


def _get_strategy_recommendation(your_price: float, avg_price: float, 
                                optimal_price: float) -> str:
    """Get strategy recommendation."""
    if abs(your_price - optimal_price) < 5:
        return "Maintain current pricing strategy"
    elif your_price < optimal_price:
        return f"Opportunity to increase price to ${optimal_price:.2f}"
    else:
        return f"Consider lowering price to ${optimal_price:.2f} to improve market share"


def _get_competitive_positioning(your_price: float, min_price: float, 
                                avg_price: float, max_price: float) -> Dict[str, str]:
    """Get competitive positioning information."""
    percentile = ((your_price - min_price) / (max_price - min_price) * 100) if max_price > min_price else 50
    
    if percentile < 25:
        position_type = "Budget Leader"
    elif percentile < 50:
        position_type = "Value Player"
    elif percentile < 75:
        position_type = "Premium Standard"
    else:
        position_type = "Premium Leader"
    
    return {
        "positioning": position_type,
        "market_percentile": f"{percentile:.1f}%",
        "recommendation": f"You are positioned as a {position_type} in the market"
    }


@router.get(
    "/health",
    summary="Check Competitor Service Health",
    description="Check if competitor analysis service is operational"
)
async def competitor_health():
    """
    Health check endpoint for competitor analysis service.
    """
    try:
        health_status = {
            "status": "healthy",
            "service": "competitor_analysis",
            "timestamp": None
        }
        
        logger.info(f"Health check: {health_status}")
        return health_status
        
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")
