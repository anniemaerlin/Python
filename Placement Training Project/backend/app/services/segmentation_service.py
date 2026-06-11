"""
Customer segmentation service module.
Handles customer classification and personalized pricing.
"""

import numpy as np
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class SegmentationService:
    """Service for customer segmentation and personalized pricing."""
    
    # Segment definitions
    SEGMENTS = {
        "VIP": {
            "description": "High-value, loyal customers with high purchase frequency",
            "price_elasticity": -0.5,
            "recommended_discount": 5,
            "retention_probability": 0.95
        },
        "Regular": {
            "description": "Regular customers with consistent purchase pattern",
            "price_elasticity": -1.0,
            "recommended_discount": 3,
            "retention_probability": 0.75
        },
        "Budget_Conscious": {
            "description": "Price-sensitive customers who respond to discounts",
            "price_elasticity": -2.0,
            "recommended_discount": 15,
            "retention_probability": 0.6
        },
        "Inactive": {
            "description": "Customers with low activity, need re-engagement",
            "price_elasticity": -1.5,
            "recommended_discount": 20,
            "retention_probability": 0.4
        },
        "New": {
            "description": "New customers, acquisition phase",
            "price_elasticity": -1.8,
            "recommended_discount": 10,
            "retention_probability": 0.5
        }
    }
    
    @staticmethod
    def segment_customer(customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify customer into segment based on behavioral data.
        
        Args:
            customer_data: Customer profile data
            
        Returns:
            Dictionary with segment classification and recommendations
        """
        try:
            # Extract metrics
            purchase_frequency = customer_data.get('purchase_frequency', 0)
            avg_order_value = customer_data.get('average_order_value', 0)
            customer_lifetime_value = customer_data.get('customer_lifetime_value', 0)
            loyalty_score = customer_data.get('loyalty_score', 0)
            days_since_purchase = customer_data.get('days_since_purchase', 365)
            
            # Calculate segment score
            segment = SegmentationService._classify_segment(
                purchase_frequency,
                avg_order_value,
                customer_lifetime_value,
                loyalty_score,
                days_since_purchase
            )
            
            # Get segment details
            segment_info = SegmentationService.SEGMENTS.get(segment, SegmentationService.SEGMENTS["Regular"])
            
            result = {
                "segment": segment,
                "segment_description": segment_info["description"],
                "recommended_price_elasticity": segment_info["price_elasticity"],
                "recommended_discount": segment_info["recommended_discount"],
                "retention_probability": segment_info["retention_probability"],
                "customer_metrics": {
                    "purchase_frequency": purchase_frequency,
                    "average_order_value": round(avg_order_value, 2),
                    "customer_lifetime_value": round(customer_lifetime_value, 2),
                    "loyalty_score": round(loyalty_score, 4),
                    "days_since_purchase": days_since_purchase
                },
                "personalized_pricing_strategy": SegmentationService._get_pricing_strategy(
                    segment, avg_order_value
                ),
                "retention_actions": SegmentationService._get_retention_actions(segment),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Customer segmented as {segment}")
            return result
            
        except Exception as e:
            logger.error(f"Error segmenting customer: {str(e)}")
            raise
    
    @staticmethod
    def _classify_segment(purchase_frequency: int, avg_order_value: float,
                         customer_lifetime_value: float, loyalty_score: float,
                         days_since_purchase: int) -> str:
        """
        Classify customer into segment using scoring logic.
        
        Args:
            purchase_frequency: Number of purchases
            avg_order_value: Average order value
            customer_lifetime_value: Total value generated
            loyalty_score: Loyalty metric (0-1)
            days_since_purchase: Days since last purchase
            
        Returns:
            Segment name
        """
        # Inactive customers
        if days_since_purchase > 180:
            return "Inactive"
        
        # New customers
        if purchase_frequency <= 2:
            return "New"
        
        # VIP customers (high CLV, high loyalty, high frequency)
        if customer_lifetime_value > 5000 and loyalty_score > 0.8 and purchase_frequency > 10:
            return "VIP"
        
        # Budget conscious (low AOV, high frequency)
        if avg_order_value < 100 and purchase_frequency > 8:
            return "Budget_Conscious"
        
        # Default: Regular customers
        return "Regular"
    
    @staticmethod
    def _get_pricing_strategy(segment: str, avg_order_value: float) -> Dict[str, Any]:
        """
        Generate personalized pricing strategy for segment.
        
        Args:
            segment: Customer segment
            avg_order_value: Average order value
            
        Returns:
            Pricing strategy dictionary
        """
        strategies = {
            "VIP": {
                "base_discount": 5,
                "promotional_strategy": "Premium products with exclusive offers",
                "price_points": ["Premium", "Luxury"],
                "recommended_actions": [
                    "Offer loyalty rewards",
                    "Provide early access to new products",
                    "Create exclusive deals",
                    "Personalize recommendations"
                ]
            },
            "Regular": {
                "base_discount": 3,
                "promotional_strategy": "Standard pricing with occasional promotions",
                "price_points": ["Standard", "Mid-range"],
                "recommended_actions": [
                    "Maintain consistent pricing",
                    "Offer seasonal promotions",
                    "Bundle popular items",
                    "Send personalized recommendations"
                ]
            },
            "Budget_Conscious": {
                "base_discount": 15,
                "promotional_strategy": "Aggressive discounts and bulk offers",
                "price_points": ["Budget", "Discount"],
                "recommended_actions": [
                    "Offer volume discounts",
                    "Create bundle deals",
                    "Highlight savings",
                    "Run flash sales"
                ]
            },
            "Inactive": {
                "base_discount": 20,
                "promotional_strategy": "Win-back campaign with aggressive incentives",
                "price_points": ["Special", "Clearance"],
                "recommended_actions": [
                    "Send re-engagement email",
                    "Offer special comeback discount",
                    "Highlight new products",
                    "Simplify repurchase process"
                ]
            },
            "New": {
                "base_discount": 10,
                "promotional_strategy": "Welcome offers and incentives",
                "price_points": ["Intro", "Standard"],
                "recommended_actions": [
                    "Provide first-purchase discount",
                    "Offer free shipping",
                    "Send welcome email series",
                    "Encourage second purchase"
                ]
            }
        }
        
        return strategies.get(segment, strategies["Regular"])
    
    @staticmethod
    def _get_retention_actions(segment: str) -> List[str]:
        """
        Get retention actions for each segment.
        
        Args:
            segment: Customer segment
            
        Returns:
            List of retention actions
        """
        actions = {
            "VIP": [
                "Schedule quarterly check-ins",
                "Provide exclusive customer service",
                "Invite to VIP events",
                "Offer priority support",
                "Create referral incentive program"
            ],
            "Regular": [
                "Send monthly newsletters",
                "Offer birthday discounts",
                "Create loyalty program",
                "Send purchase reminders",
                "Ask for product reviews"
            ],
            "Budget_Conscious": [
                "Send discount alerts",
                "Highlight clearance items",
                "Create price-drop notifications",
                "Offer bulk discounts",
                "Provide comparison tools"
            ],
            "Inactive": [
                "Send re-engagement email",
                "Offer special comeback discount",
                "Survey why they left",
                "Highlight product improvements",
                "Provide new product showcase"
            ],
            "New": [
                "Send onboarding tutorial",
                "Offer guided product tour",
                "Provide quick-start guide",
                "Ask for feedback",
                "Incentivize second purchase"
            ]
        }
        
        return actions.get(segment, actions["Regular"])
    
    @staticmethod
    def predict_churn_probability(customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict customer churn probability.
        
        Args:
            customer_data: Customer profile data
            
        Returns:
            Dictionary with churn prediction
        """
        try:
            # Extract metrics
            days_since_purchase = customer_data.get('days_since_purchase', 365)
            purchase_frequency = customer_data.get('purchase_frequency', 0)
            avg_order_value = customer_data.get('average_order_value', 0)
            loyalty_score = customer_data.get('loyalty_score', 0)
            customer_lifetime_value = customer_data.get('customer_lifetime_value', 0)
            
            # Calculate churn probability (0-1)
            churn_prob = 0.0
            
            # Factor 1: Days since purchase (significant factor)
            if days_since_purchase > 180:
                churn_prob += 0.5
            elif days_since_purchase > 90:
                churn_prob += 0.25
            elif days_since_purchase > 30:
                churn_prob += 0.1
            
            # Factor 2: Purchase frequency
            if purchase_frequency < 2:
                churn_prob += 0.3
            elif purchase_frequency < 5:
                churn_prob += 0.1
            
            # Factor 3: Loyalty score
            if loyalty_score < 0.3:
                churn_prob += 0.2
            elif loyalty_score > 0.8:
                churn_prob -= 0.2
            
            # Factor 4: Customer lifetime value
            if customer_lifetime_value < 500:
                churn_prob += 0.1
            
            # Normalize to 0-1 range
            churn_prob = max(0, min(churn_prob, 1.0))
            
            # Determine risk level
            if churn_prob > 0.7:
                risk_level = "High"
            elif churn_prob > 0.4:
                risk_level = "Medium"
            else:
                risk_level = "Low"
            
            result = {
                "churn_probability": round(churn_prob, 4),
                "risk_level": risk_level,
                "risk_factors": SegmentationService._identify_risk_factors(customer_data),
                "recommended_interventions": SegmentationService._get_interventions(risk_level),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Churn prediction calculated: {risk_level} risk")
            return result
            
        except Exception as e:
            logger.error(f"Error predicting churn: {str(e)}")
            raise
    
    @staticmethod
    def _identify_risk_factors(customer_data: Dict[str, Any]) -> List[str]:
        """Identify factors contributing to churn risk."""
        risk_factors = []
        
        if customer_data.get('days_since_purchase', 365) > 90:
            risk_factors.append("Inactive for more than 90 days")
        
        if customer_data.get('purchase_frequency', 0) < 3:
            risk_factors.append("Low purchase frequency")
        
        if customer_data.get('loyalty_score', 0) < 0.5:
            risk_factors.append("Low loyalty score")
        
        if customer_data.get('average_order_value', 0) < 100:
            risk_factors.append("Low average order value")
        
        if customer_data.get('customer_lifetime_value', 0) < 500:
            risk_factors.append("Low customer lifetime value")
        
        return risk_factors
    
    @staticmethod
    def _get_interventions(risk_level: str) -> List[str]:
        """Get recommended interventions for risk level."""
        interventions = {
            "High": [
                "Send urgent re-engagement email",
                "Offer special one-time discount (20-30%)",
                "Provide personalized product recommendations",
                "Offer free shipping on next order",
                "Assign dedicated customer service representative"
            ],
            "Medium": [
                "Send reminder email about products they viewed",
                "Offer moderate discount (10-15%)",
                "Create personalized bundle deal",
                "Ask for feedback on recent purchase",
                "Share new arrival notifications"
            ],
            "Low": [
                "Continue regular communications",
                "Offer loyalty rewards",
                "Share exclusive content",
                "Invite to community events",
                "Request product reviews"
            ]
        }
        
        return interventions.get(risk_level, interventions["Low"])
