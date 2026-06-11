"""
Pricing service module.
Handles ML model loading, predictions, and pricing logic.
"""

import joblib
import numpy as np
import pandas as pd
import logging
from typing import Dict, Any, Tuple, List
import os
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class PricingService:
    """Service for dynamic pricing predictions and revenue simulations."""
    
    _xgboost_model = None
    _random_forest_model = None
    _models_loaded = False
    _feature_names = [
        'current_price',
        'competitor_price',
        'demand',
        'inventory',
        'conversion_rate',
        'promotion',
        'discount_percent',
        'demand_index'
    ]
    
    @classmethod
    def load_models(cls, model_dir: str = None) -> bool:
        """
        Load ML models from disk.
        
        Args:
            model_dir: Directory containing model files
            
        Returns:
            bool: True if models loaded successfully
        """
        try:
            if model_dir is None:
                model_dir = Path(__file__).parent.parent / "models"
            
            model_dir = Path(model_dir)
            
            # For demonstration, create mock models if they don't exist
            xgboost_path = model_dir / "xgboost_model.pkl"
            random_forest_path = model_dir / "random_forest_model.pkl"
            
            # Load or create models
            if xgboost_path.exists():
                cls._xgboost_model = joblib.load(xgboost_path)
                logger.info("XGBoost model loaded successfully")
            else:
                cls._create_mock_model(xgboost_path, "xgboost")
                cls._xgboost_model = joblib.load(xgboost_path)
                logger.info("XGBoost model created and loaded")
            
            if random_forest_path.exists():
                cls._random_forest_model = joblib.load(random_forest_path)
                logger.info("Random Forest model loaded successfully")
            else:
                cls._create_mock_model(random_forest_path, "random_forest")
                cls._random_forest_model = joblib.load(random_forest_path)
                logger.info("Random Forest model created and loaded")
            
            cls._models_loaded = True
            return True
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            cls._models_loaded = False
            return False
    
    @classmethod
    def _create_mock_model(cls, model_path: Path, model_type: str) -> None:
        """
        Create a mock model for demonstration purposes.
        In production, use actual trained models.
        
        Args:
            model_path: Path to save the model
            model_type: Type of model (xgboost or random_forest)
        """
        try:
            from sklearn.ensemble import RandomForestRegressor
            try:
                import xgboost as xgb
            except ImportError:
                xgb = None
            
            # Create training data
            np.random.seed(42)
            X_train = np.random.randn(100, len(cls._feature_names))
            y_train = 800 + 0.5 * X_train[:, 0] + np.random.randn(100) * 50
            
            if model_type == "xgboost" and xgb:
                model = xgb.XGBRegressor(n_estimators=100, max_depth=5, random_state=42)
            else:
                model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
            
            model.fit(X_train, y_train)
            model_path.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(model, model_path)
            logger.info(f"Mock {model_type} model created at {model_path}")
            
        except Exception as e:
            logger.error(f"Error creating mock model: {str(e)}")
    
    @classmethod
    def predict_price(cls, pricing_data: Dict[str, Any], model_choice: str = "xgboost") -> Dict[str, Any]:
        """
        Predict optimal price using ML model.
        
        Args:
            pricing_data: Dictionary containing pricing input features
            model_choice: Which model to use (xgboost or random_forest)
            
        Returns:
            Dictionary with prediction results
        """
        try:
            if not cls._models_loaded:
                logger.warning("Models not loaded, attempting to load...")
                cls.load_models()
            
            # Prepare features
            features = [
                pricing_data.get('current_price'),
                pricing_data.get('competitor_price'),
                pricing_data.get('demand'),
                pricing_data.get('inventory'),
                pricing_data.get('conversion_rate'),
                pricing_data.get('promotion'),
                pricing_data.get('discount_percent'),
                pricing_data.get('demand_index')
            ]
            
            X = np.array(features).reshape(1, -1)
            
            # Select model
            if model_choice == "xgboost" and cls._xgboost_model:
                model = cls._xgboost_model
                model_name = "XGBoost"
            else:
                model = cls._random_forest_model
                model_name = "Random Forest"
            
            # Make prediction
            predicted_price = float(model.predict(X)[0])
            
            # Ensure predicted price is reasonable (between 50% and 150% of current price)
            min_price = pricing_data['current_price'] * 0.5
            max_price = pricing_data['current_price'] * 1.5
            predicted_price = max(min_price, min(max_price, predicted_price))
            
            # Calculate confidence score (simulated)
            confidence_score = cls._calculate_confidence_score(pricing_data, predicted_price)
            
            # Calculate price change
            price_change_percent = ((predicted_price - pricing_data['current_price']) / 
                                   pricing_data['current_price']) * 100
            
            # Estimate revenue impact
            estimated_demand_change = cls._estimate_demand_change(
                price_change_percent,
                pricing_data.get('demand_index', 0.5)
            )
            revenue_impact = (predicted_price * pricing_data['demand'] * estimated_demand_change - 
                            pricing_data['current_price'] * pricing_data['demand'])
            
            result = {
                "recommended_price": round(predicted_price, 2),
                "model_used": model_name,
                "confidence_score": round(confidence_score, 2),
                "price_change_percent": round(price_change_percent, 2),
                "revenue_impact": round(revenue_impact, 2),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Price prediction successful: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error predicting price: {str(e)}")
            raise
    
    @classmethod
    def predict_price_with_explanation(cls, pricing_data: Dict[str, Any], 
                                      model_choice: str = "xgboost") -> Dict[str, Any]:
        """
        Predict price with feature importance explanation (Explainable AI).
        
        Args:
            pricing_data: Dictionary containing pricing input features
            model_choice: Which model to use
            
        Returns:
            Dictionary with prediction and feature importance
        """
        try:
            # Get base prediction
            prediction = cls.predict_price(pricing_data, model_choice)
            
            # Select model
            if model_choice == "xgboost" and cls._xgboost_model:
                model = cls._xgboost_model
            else:
                model = cls._random_forest_model
            
            # Get feature importance
            try:
                if hasattr(model, 'feature_importances_'):
                    importances = model.feature_importances_
                else:
                    importances = np.ones(len(cls._feature_names)) / len(cls._feature_names)
            except:
                importances = np.ones(len(cls._feature_names)) / len(cls._feature_names)
            
            # Create feature importance dictionary
            feature_importance = {
                name: float(importance) 
                for name, importance in zip(cls._feature_names, importances)
            }
            
            # Sort and get top factors
            sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            top_factors = cls._generate_top_factors(pricing_data, sorted_features[:3])
            
            # Generate explanation
            explanation = cls._generate_explanation(pricing_data, prediction, sorted_features)
            
            result = {
                **prediction,
                "feature_importance": feature_importance,
                "top_factors": top_factors,
                "explanation": explanation
            }
            
            logger.info("Price prediction with explanation generated successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            raise
    
    @classmethod
    def simulate_revenue_impact(cls, current_price: float, current_demand: int,
                               proposed_price: float, price_elasticity: float) -> Dict[str, Any]:
        """
        Simulate revenue impact of price change.
        
        Args:
            current_price: Current price
            current_demand: Current demand
            proposed_price: Proposed new price
            price_elasticity: Price elasticity of demand
            
        Returns:
            Dictionary with revenue simulation results
        """
        try:
            # Calculate current revenue
            current_revenue = current_price * current_demand
            
            # Calculate percentage price change
            price_change_percent = ((proposed_price - current_price) / current_price) * 100
            
            # Calculate new demand using elasticity formula
            # New Quantity = Old Quantity * (1 + elasticity * price_change_percent / 100)
            demand_change_percent = price_elasticity * (price_change_percent / 100)
            new_demand = int(current_demand * (1 + demand_change_percent))
            new_demand = max(1, new_demand)  # Ensure at least 1 unit demand
            
            # Calculate projected revenue
            projected_revenue = proposed_price * new_demand
            
            # Calculate revenue change
            revenue_change = projected_revenue - current_revenue
            revenue_change_percent = (revenue_change / current_revenue) * 100 if current_revenue > 0 else 0
            
            # Generate recommendation
            if revenue_change > 0:
                recommendation = f"Increase price to ${proposed_price}. Expected revenue increase: ${revenue_change:,.2f} ({revenue_change_percent:.2f}%)"
            elif revenue_change < 0:
                recommendation = f"Consider keeping current price of ${current_price}. Proposed increase would decrease revenue by ${abs(revenue_change):,.2f} ({abs(revenue_change_percent):.2f}%)"
            else:
                recommendation = "Revenue would remain unchanged with proposed price."
            
            result = {
                "current_revenue": round(current_revenue, 2),
                "projected_revenue": round(projected_revenue, 2),
                "revenue_change_percent": round(revenue_change_percent, 2),
                "projected_demand": new_demand,
                "recommendation": recommendation,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Revenue simulation successful: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error simulating revenue: {str(e)}")
            raise
    
    @classmethod
    def _calculate_confidence_score(cls, pricing_data: Dict[str, Any], 
                                   predicted_price: float) -> float:
        """
        Calculate confidence score for the prediction.
        
        Args:
            pricing_data: Input pricing data
            predicted_price: Predicted price
            
        Returns:
            Confidence score (0-100)
        """
        # Base confidence
        confidence = 85.0
        
        # Adjust based on data quality
        if pricing_data['demand'] > 0:
            confidence += 5
        
        if 0 < pricing_data['inventory'] < 100:
            confidence += 3
        
        if pricing_data['conversion_rate'] > 0.1:
            confidence += 3
        
        # Adjust based on price reasonableness
        price_ratio = predicted_price / pricing_data['current_price']
        if 0.8 <= price_ratio <= 1.2:
            confidence += 4
        
        return min(confidence, 99.99)
    
    @classmethod
    def _estimate_demand_change(cls, price_change_percent: float, 
                               demand_index: float) -> float:
        """
        Estimate demand change based on price change.
        
        Args:
            price_change_percent: Percentage change in price
            demand_index: Current demand index
            
        Returns:
            Demand multiplier
        """
        # Price elasticity varies with demand level
        if demand_index > 0.7:
            elasticity = -1.2
        elif demand_index > 0.4:
            elasticity = -0.8
        else:
            elasticity = -0.5
        
        demand_change = 1 + (elasticity * price_change_percent / 100)
        return max(0.5, min(demand_change, 1.5))  # Constrain between 0.5x and 1.5x
    
    @classmethod
    def _generate_top_factors(cls, pricing_data: Dict[str, Any], 
                             sorted_features: List[Tuple[str, float]]) -> List[str]:
        """
        Generate human-readable top factors.
        
        Args:
            pricing_data: Input pricing data
            sorted_features: Sorted features by importance
            
        Returns:
            List of factor descriptions
        """
        factors = []
        feature_values = {
            'demand': pricing_data['demand'],
            'inventory': pricing_data['inventory'],
            'competitor_price': pricing_data['competitor_price'],
            'conversion_rate': pricing_data['conversion_rate'],
            'current_price': pricing_data['current_price']
        }
        
        for feature_name, importance in sorted_features[:3]:
            if feature_name in feature_values:
                value = feature_values[feature_name]
                
                if feature_name == 'demand':
                    level = "High" if value > 150 else "Medium" if value > 50 else "Low"
                    factors.append(f"{level} demand detected ({int(value)} units)")
                elif feature_name == 'inventory':
                    level = "Low" if value < 30 else "Medium" if value < 100 else "High"
                    factors.append(f"{level} inventory ({int(value)} units)")
                elif feature_name == 'competitor_price':
                    diff = value - pricing_data['current_price']
                    if diff < 0:
                        factors.append(f"Competitor price is lower (${value:.2f} vs ${pricing_data['current_price']:.2f})")
                    elif diff > 0:
                        factors.append(f"Competitor price is higher (${value:.2f} vs ${pricing_data['current_price']:.2f})")
                elif feature_name == 'conversion_rate':
                    factors.append(f"Conversion rate: {value*100:.1f}%")
                elif feature_name == 'current_price':
                    factors.append(f"Current price: ${value:.2f}")
        
        return factors
    
    @classmethod
    def _generate_explanation(cls, pricing_data: Dict[str, Any], 
                            prediction: Dict[str, Any],
                            sorted_features: List[Tuple[str, float]]) -> str:
        """
        Generate human-readable explanation.
        
        Args:
            pricing_data: Input pricing data
            prediction: Prediction results
            sorted_features: Sorted features by importance
            
        Returns:
            Explanation string
        """
        price_change = prediction['price_change_percent']
        direction = "increased" if price_change > 0 else "decreased" if price_change < 0 else "unchanged"
        top_factor = sorted_features[0][0] if sorted_features else "overall market conditions"
        
        explanation = f"Price {direction} by {abs(price_change):.1f}% primarily due to {top_factor}. "
        
        if pricing_data['inventory'] < 30:
            explanation += "Low inventory suggests price increase opportunity. "
        
        if pricing_data['demand'] > 150:
            explanation += "High demand supports premium pricing. "
        
        if pricing_data['competitor_price'] < pricing_data['current_price']:
            explanation += "Maintain competitive advantage while optimizing margins. "
        
        explanation += f"Confidence in this recommendation: {prediction['confidence_score']:.1f}%"
        
        return explanation
    
    @classmethod
    def are_models_loaded(cls) -> bool:
        """Check if models are loaded."""
        return cls._models_loaded
