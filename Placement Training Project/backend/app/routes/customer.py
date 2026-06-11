"""
Customer segmentation routes module.
Endpoints for customer classification and personalized pricing.
"""

from fastapi import APIRouter, HTTPException, Body
import logging
from typing import Dict, Any
from app.services.segmentation_service import SegmentationService
from app.database.firebase import FirebaseDB

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/customer", tags=["Customer Segmentation"])


@router.post(
    "/segment",
    summary="Segment Customer",
    description="Classify customer into segment and get personalized recommendations"
)
async def segment_customer(
    customer_data: Dict[str, Any] = Body(
        ...,
        example={
            "purchase_frequency": 12,
            "average_order_value": 500,
            "customer_lifetime_value": 6000,
            "loyalty_score": 0.85
        }
    )
):
    """
    Classify customer into a segment based on behavioral data.
    
    Input parameters:
    - **purchase_frequency**: Number of purchases
    - **average_order_value**: Average order value
    - **customer_lifetime_value**: Total value from customer
    - **loyalty_score**: Loyalty metric (0-1)
    - **days_since_purchase**: (Optional) Days since last purchase
    
    Returns:
    - Customer segment (VIP, Regular, Budget_Conscious, Inactive, New)
    - Segment description
    - Recommended price elasticity
    - Recommended discount percentage
    - Retention probability
    - Personalized pricing strategy
    - Retention actions
    """
    try:
        logger.info("Customer segmentation requested")
        
        # Validate required fields
        required_fields = ['purchase_frequency', 'average_order_value', 'customer_lifetime_value', 'loyalty_score']
        for field in required_fields:
            if field not in customer_data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required field: {field}"
                )
        
        # Validate data types and ranges
        if not isinstance(customer_data['purchase_frequency'], (int, float)) or customer_data['purchase_frequency'] < 0:
            raise HTTPException(status_code=400, detail="purchase_frequency must be a positive number")
        
        if not isinstance(customer_data['average_order_value'], (int, float)) or customer_data['average_order_value'] < 0:
            raise HTTPException(status_code=400, detail="average_order_value must be a positive number")
        
        if not isinstance(customer_data['customer_lifetime_value'], (int, float)) or customer_data['customer_lifetime_value'] < 0:
            raise HTTPException(status_code=400, detail="customer_lifetime_value must be a positive number")
        
        if not isinstance(customer_data['loyalty_score'], (int, float)) or not (0 <= customer_data['loyalty_score'] <= 1):
            raise HTTPException(status_code=400, detail="loyalty_score must be between 0 and 1")
        
        # Set default for days_since_purchase if not provided
        if 'days_since_purchase' not in customer_data:
            customer_data['days_since_purchase'] = 30
        
        # Get segmentation
        segment_result = SegmentationService.segment_customer(customer_data)
        
        # Save to database
        customer_id = customer_data.get('customer_id', f"cust_{segment_result['timestamp']}")
        FirebaseDB.save_customer_segment(
            customer_id=customer_id,
            segment_data=segment_result
        )
        
        logger.info(f"Customer segmented as: {segment_result['segment']}")
        return segment_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error segmenting customer: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/churn-prediction",
    summary="Predict Customer Churn",
    description="Predict probability of customer churn"
)
async def predict_churn(
    customer_data: Dict[str, Any] = Body(
        ...,
        example={
            "purchase_frequency": 5,
            "average_order_value": 250,
            "customer_lifetime_value": 2000,
            "loyalty_score": 0.4,
            "days_since_purchase": 120
        }
    )
):
    """
    Predict the probability of customer churn.
    
    Input parameters:
    - **purchase_frequency**: Number of purchases
    - **average_order_value**: Average order value
    - **customer_lifetime_value**: Total value from customer
    - **loyalty_score**: Loyalty metric (0-1)
    - **days_since_purchase**: (Optional) Days since last purchase
    
    Returns:
    - Churn probability (0-1)
    - Risk level (Low, Medium, High)
    - Risk factors identified
    - Recommended interventions
    """
    try:
        logger.info("Churn prediction requested")
        
        # Validate required fields
        required_fields = ['purchase_frequency', 'average_order_value', 'customer_lifetime_value', 'loyalty_score']
        for field in required_fields:
            if field not in customer_data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required field: {field}"
                )
        
        # Set default for days_since_purchase if not provided
        if 'days_since_purchase' not in customer_data:
            customer_data['days_since_purchase'] = 30
        
        # Predict churn
        churn_result = SegmentationService.predict_churn_probability(customer_data)
        
        logger.info(f"Churn prediction completed: {churn_result['risk_level']} risk")
        return churn_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error predicting churn: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/segments",
    summary="Get Segment Definitions",
    description="Get information about all customer segments"
)
async def get_segments():
    """
    Get detailed information about all customer segments and their characteristics.
    
    Returns information for each segment:
    - VIP
    - Regular
    - Budget_Conscious
    - Inactive
    - New
    """
    try:
        logger.info("Segment definitions requested")
        
        segments_info = {
            segment_name: {
                "description": segment_info["description"],
                "price_elasticity": segment_info["price_elasticity"],
                "recommended_discount": segment_info["recommended_discount"],
                "retention_probability": segment_info["retention_probability"]
            }
            for segment_name, segment_info in SegmentationService.SEGMENTS.items()
        }
        
        return segments_info
        
    except Exception as e:
        logger.error(f"Error getting segment definitions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/health",
    summary="Check Customer Service Health",
    description="Check if customer segmentation service is operational"
)
async def customer_health():
    """
    Health check endpoint for customer segmentation service.
    """
    try:
        health_status = {
            "status": "healthy",
            "service": "customer_segmentation",
            "timestamp": None
        }
        
        logger.info(f"Health check: {health_status}")
        return health_status
        
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")
