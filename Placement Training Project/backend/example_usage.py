"""
Example usage script for the Dynamic Pricing Engine API.
Demonstrates how to use the API programmatically.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

class DynamicPricingClient:
    """Client for interacting with Dynamic Pricing Engine API."""
    
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def predict_price(self, current_price, competitor_price, demand, 
                     inventory, conversion_rate, promotion=0, 
                     discount_percent=0, demand_index=0.5):
        """
        Get AI-recommended optimal price.
        
        Args:
            current_price: Current product price
            competitor_price: Competitor's price
            demand: Current demand
            inventory: Available inventory
            conversion_rate: Conversion rate (0-1)
            promotion: Is promotion active (0 or 1)
            discount_percent: Current discount %
            demand_index: Demand index (0-1)
        
        Returns:
            Prediction response
        """
        payload = {
            "current_price": current_price,
            "competitor_price": competitor_price,
            "demand": demand,
            "inventory": inventory,
            "conversion_rate": conversion_rate,
            "promotion": promotion,
            "discount_percent": discount_percent,
            "demand_index": demand_index
        }
        
        response = self.session.post(f"{self.base_url}/pricing/predict", json=payload)
        return response.json()
    
    def predict_price_with_explanation(self, current_price, competitor_price, 
                                      demand, inventory, conversion_rate, 
                                      promotion=0, discount_percent=0, 
                                      demand_index=0.5):
        """Get price prediction with feature importance explanation."""
        payload = {
            "current_price": current_price,
            "competitor_price": competitor_price,
            "demand": demand,
            "inventory": inventory,
            "conversion_rate": conversion_rate,
            "promotion": promotion,
            "discount_percent": discount_percent,
            "demand_index": demand_index
        }
        
        response = self.session.post(
            f"{self.base_url}/pricing/predict-with-explanation",
            json=payload
        )
        return response.json()
    
    def simulate_revenue(self, current_price, current_demand, proposed_price, 
                        price_elasticity):
        """
        Simulate revenue impact of price change.
        
        Args:
            current_price: Current price
            current_demand: Current demand
            proposed_price: Proposed new price
            price_elasticity: Price elasticity of demand
        
        Returns:
            Revenue simulation results
        """
        payload = {
            "current_price": current_price,
            "current_demand": current_demand,
            "proposed_price": proposed_price,
            "price_elasticity": price_elasticity
        }
        
        response = self.session.post(f"{self.base_url}/pricing/simulate-revenue", json=payload)
        return response.json()
    
    def forecast_demand(self, product_id, historical_demand, days_ahead=30, 
                       seasonality="none"):
        """
        Forecast future demand.
        
        Args:
            product_id: Product identifier
            historical_demand: List of historical demand values
            days_ahead: Days to forecast (1-365)
            seasonality: Pattern (none, weekly, monthly)
        
        Returns:
            Forecast results
        """
        payload = {
            "product_id": product_id,
            "historical_demand": historical_demand,
            "days_ahead": days_ahead,
            "seasonality": seasonality
        }
        
        response = self.session.post(f"{self.base_url}/forecast/demand", json=payload)
        return response.json()
    
    def get_demand_insights(self, product_id, historical_demand):
        """Get insights from historical demand data."""
        response = self.session.post(
            f"{self.base_url}/forecast/insights",
            params={
                "product_id": product_id,
                "historical_demand": historical_demand
            }
        )
        return response.json()
    
    def inventory_recommendation(self, product_id, forecasted_demand):
        """Get inventory level recommendations."""
        response = self.session.post(
            f"{self.base_url}/forecast/inventory-recommendation",
            params={
                "product_id": product_id,
                "forecasted_demand": forecasted_demand
            }
        )
        return response.json()
    
    def segment_customer(self, purchase_frequency, average_order_value, 
                        customer_lifetime_value, loyalty_score, 
                        days_since_purchase=30):
        """
        Classify customer into segment.
        
        Args:
            purchase_frequency: Number of purchases
            average_order_value: Average order value
            customer_lifetime_value: Total value from customer
            loyalty_score: Loyalty metric (0-1)
            days_since_purchase: Days since last purchase
        
        Returns:
            Customer segment and recommendations
        """
        payload = {
            "purchase_frequency": purchase_frequency,
            "average_order_value": average_order_value,
            "customer_lifetime_value": customer_lifetime_value,
            "loyalty_score": loyalty_score,
            "days_since_purchase": days_since_purchase
        }
        
        response = self.session.post(f"{self.base_url}/customer/segment", json=payload)
        return response.json()
    
    def predict_churn(self, purchase_frequency, average_order_value, 
                     customer_lifetime_value, loyalty_score, 
                     days_since_purchase=30):
        """Predict customer churn probability."""
        payload = {
            "purchase_frequency": purchase_frequency,
            "average_order_value": average_order_value,
            "customer_lifetime_value": customer_lifetime_value,
            "loyalty_score": loyalty_score,
            "days_since_purchase": days_since_purchase
        }
        
        response = self.session.post(f"{self.base_url}/customer/churn-prediction", json=payload)
        return response.json()
    
    def analyze_competitors(self, product_id, your_current_price, competitor_prices):
        """
        Analyze competitor prices.
        
        Args:
            product_id: Product identifier
            your_current_price: Your current price
            competitor_prices: Dict of competitor names and prices
        
        Returns:
            Competitor analysis results
        """
        payload = {
            "product_id": product_id,
            "your_current_price": your_current_price,
            "competitor_prices": competitor_prices
        }
        
        response = self.session.post(f"{self.base_url}/competitor/analyze", json=payload)
        return response.json()
    
    def get_segments(self):
        """Get all customer segment definitions."""
        response = self.session.get(f"{self.base_url}/customer/segments")
        return response.json()
    
    def health_check(self):
        """Check API health status."""
        response = self.session.get(f"{self.base_url.replace('/v1', '')}/health")
        return response.json()


def main():
    """Example usage of the Dynamic Pricing Client."""
    
    print("=" * 60)
    print("Dynamic Pricing Engine - Example Usage")
    print("=" * 60)
    print()
    
    # Initialize client
    client = DynamicPricingClient()
    
    print("1. Checking API Health...")
    health = client.health_check()
    print(f"   Status: {health['status']}")
    print()
    
    print("2. Predicting Optimal Price...")
    price_prediction = client.predict_price(
        current_price=1000,
        competitor_price=950,
        demand=200,
        inventory=50,
        conversion_rate=0.12,
        promotion=1,
        discount_percent=10,
        demand_index=0.75
    )
    print(f"   Recommended Price: ${price_prediction['recommended_price']}")
    print(f"   Model Used: {price_prediction['model_used']}")
    print(f"   Confidence: {price_prediction['confidence_score']}%")
    print(f"   Price Change: {price_prediction['price_change_percent']}%")
    print()
    
    print("3. Getting Price Prediction with Explanation...")
    explanation = client.predict_price_with_explanation(
        current_price=1000,
        competitor_price=950,
        demand=200,
        inventory=50,
        conversion_rate=0.12,
        promotion=1,
        discount_percent=10,
        demand_index=0.75
    )
    print(f"   Explanation: {explanation['explanation']}")
    print(f"   Top Factors: {', '.join(explanation['top_factors'][:2])}")
    print()
    
    print("4. Simulating Revenue Impact...")
    revenue_sim = client.simulate_revenue(
        current_price=1000,
        current_demand=100,
        proposed_price=1100,
        price_elasticity=-1.5
    )
    print(f"   Current Revenue: ${revenue_sim['current_revenue']:,.2f}")
    print(f"   Projected Revenue: ${revenue_sim['projected_revenue']:,.2f}")
    print(f"   Change: {revenue_sim['revenue_change_percent']}%")
    print()
    
    print("5. Forecasting Demand...")
    forecast = client.forecast_demand(
        product_id="PROD001",
        historical_demand=[100, 110, 120, 115, 130, 125, 140],
        days_ahead=30,
        seasonality="weekly"
    )
    print(f"   Trend: {forecast['trend']}")
    print(f"   Forecast Accuracy: {forecast['prediction_accuracy']}%")
    print(f"   Next 5 Days: {forecast['forecasted_demand'][:5]}")
    print()
    
    print("6. Segmenting Customer...")
    segment = client.segment_customer(
        purchase_frequency=12,
        average_order_value=500,
        customer_lifetime_value=6000,
        loyalty_score=0.85
    )
    print(f"   Segment: {segment['segment']}")
    print(f"   Recommended Discount: {segment['recommended_discount']}%")
    print(f"   Retention Probability: {segment['retention_probability']:.0%}")
    print()
    
    print("7. Predicting Customer Churn...")
    churn = client.predict_churn(
        purchase_frequency=5,
        average_order_value=250,
        customer_lifetime_value=2000,
        loyalty_score=0.4,
        days_since_purchase=120
    )
    print(f"   Churn Probability: {churn['churn_probability']:.1%}")
    print(f"   Risk Level: {churn['risk_level']}")
    print(f"   Risk Factors: {', '.join(churn['risk_factors'][:2])}")
    print()
    
    print("8. Analyzing Competitors...")
    competitor_analysis = client.analyze_competitors(
        product_id="PROD001",
        your_current_price=1000,
        competitor_prices={
            "CompetitorA": 950,
            "CompetitorB": 980,
            "CompetitorC": 1020
        }
    )
    print(f"   Your Position: {competitor_analysis['your_price_position']}")
    print(f"   Avg Competitor Price: ${competitor_analysis['average_competitor_price']:.2f}")
    print(f"   Price Difference: {competitor_analysis['price_difference_percent']:.1f}%")
    print(f"   Recommendation: {competitor_analysis['recommended_action']}")
    print()
    
    print("=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nMake sure the API server is running at http://localhost:8000")
        print("Start it with: python -m uvicorn app.main:app --reload")
