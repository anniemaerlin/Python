"""
Demand forecasting service module.
Handles demand prediction and time series analysis.
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class DemandTrendEnum(str, Enum):
    """Demand trend classification."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ForecastService:
    """Service for demand forecasting and trend analysis."""
    
    @staticmethod
    def forecast_demand(historical_demand: List[float], days_ahead: int = 30,
                       seasonality: str = "none") -> Dict[str, Any]:
        """
        Forecast future demand using time series analysis.
        
        Args:
            historical_demand: Historical demand data
            days_ahead: Number of days to forecast
            seasonality: Seasonality pattern (none, weekly, monthly)
            
        Returns:
            Dictionary with forecast results
        """
        try:
            if not historical_demand or len(historical_demand) < 3:
                raise ValueError("Need at least 3 historical data points")
            
            # Convert to numpy array
            data = np.array(historical_demand, dtype=float)
            
            # Calculate trend
            x = np.arange(len(data))
            coeffs = np.polyfit(x, data, 1)
            trend_line = coeffs[0] * np.arange(len(data)) + coeffs[1]
            trend_slope = coeffs[0]
            
            # Calculate seasonality factor if requested
            if seasonality != "none" and len(data) > 7:
                if seasonality == "weekly":
                    seasonal_period = 7
                elif seasonality == "monthly":
                    seasonal_period = 30
                else:
                    seasonal_period = len(data)
                
                seasonal_factors = ForecastService._calculate_seasonal_factors(
                    data, seasonal_period
                )
            else:
                seasonal_factors = None
            
            # Generate forecast
            last_value = data[-1]
            forecast = []
            confidence_lower = []
            confidence_upper = []
            
            # Calculate standard deviation for confidence intervals
            residuals = data - trend_line
            std_dev = np.std(residuals)
            
            for i in range(1, days_ahead + 1):
                # Trend component
                forecasted_value = last_value + (trend_slope * i)
                
                # Add seasonal component if applicable
                if seasonal_factors is not None:
                    seasonal_idx = (len(data) + i - 1) % len(seasonal_factors)
                    forecasted_value *= seasonal_factors[seasonal_idx]
                
                # Ensure non-negative
                forecasted_value = max(0, forecasted_value)
                
                # Calculate confidence intervals
                confidence_range = 1.96 * std_dev * np.sqrt(i)
                lower = max(0, forecasted_value - confidence_range)
                upper = forecasted_value + confidence_range
                
                forecast.append(round(forecasted_value, 2))
                confidence_lower.append(round(lower, 2))
                confidence_upper.append(round(upper, 2))
            
            # Determine trend
            avg_recent = np.mean(data[-7:]) if len(data) >= 7 else np.mean(data)
            avg_historical = np.mean(data)
            
            if avg_recent > avg_historical * 1.1:
                trend = DemandTrendEnum.HIGH
            elif avg_recent < avg_historical * 0.9:
                trend = DemandTrendEnum.LOW
            else:
                trend = DemandTrendEnum.MEDIUM
            
            # Calculate model accuracy (MAE on historical data)
            mae = np.mean(np.abs(data - trend_line))
            rmse = np.sqrt(np.mean((data - trend_line) ** 2))
            accuracy = max(0, 100 - (rmse / np.mean(data) * 100)) if np.mean(data) > 0 else 0
            accuracy = min(accuracy, 99.99)
            
            result = {
                "forecasted_demand": forecast,
                "trend": trend.value,
                "confidence_interval_lower": confidence_lower,
                "confidence_interval_upper": confidence_upper,
                "prediction_accuracy": round(accuracy, 2),
                "trend_slope": round(float(trend_slope), 4),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Demand forecast generated successfully for {days_ahead} days")
            return result
            
        except Exception as e:
            logger.error(f"Error forecasting demand: {str(e)}")
            raise
    
    @staticmethod
    def _calculate_seasonal_factors(data: np.ndarray, period: int) -> np.ndarray:
        """
        Calculate seasonal adjustment factors.
        
        Args:
            data: Historical demand data
            period: Seasonal period (7 for weekly, 30 for monthly)
            
        Returns:
            Array of seasonal factors
        """
        try:
            seasonal_factors = []
            
            for i in range(period):
                indices = np.arange(i, len(data), period)
                if len(indices) > 0:
                    period_values = data[indices]
                    factor = np.mean(period_values) / np.mean(data)
                    seasonal_factors.append(max(0.5, min(factor, 1.5)))
                else:
                    seasonal_factors.append(1.0)
            
            return np.array(seasonal_factors)
        except Exception as e:
            logger.error(f"Error calculating seasonal factors: {str(e)}")
            return np.ones(period)
    
    @staticmethod
    def get_demand_insights(historical_demand: List[float]) -> Dict[str, Any]:
        """
        Generate insights from historical demand data.
        
        Args:
            historical_demand: Historical demand data
            
        Returns:
            Dictionary with demand insights
        """
        try:
            data = np.array(historical_demand, dtype=float)
            
            insights = {
                "average_demand": round(float(np.mean(data)), 2),
                "peak_demand": round(float(np.max(data)), 2),
                "minimum_demand": round(float(np.min(data)), 2),
                "demand_volatility": round(float(np.std(data)), 2),
                "demand_variance": round(float(np.var(data)), 2),
                "median_demand": round(float(np.median(data)), 2),
                "coefficient_of_variation": round(float(np.std(data) / np.mean(data)) if np.mean(data) > 0 else 0, 4),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info("Demand insights calculated successfully")
            return insights
            
        except Exception as e:
            logger.error(f"Error calculating demand insights: {str(e)}")
            raise
    
    @staticmethod
    def recommend_inventory_levels(forecasted_demand: List[float], 
                                   safety_stock_multiplier: float = 1.5) -> Dict[str, Any]:
        """
        Recommend inventory levels based on forecast.
        
        Args:
            forecasted_demand: Forecasted demand
            safety_stock_multiplier: Multiplier for safety stock
            
        Returns:
            Dictionary with inventory recommendations
        """
        try:
            demand_array = np.array(forecasted_demand, dtype=float)
            
            avg_demand = np.mean(demand_array)
            peak_demand = np.max(demand_array)
            std_dev = np.std(demand_array)
            
            # Calculate safety stock (standard deviation * service factor)
            service_factor = 1.65  # ~95% service level
            safety_stock = safety_stock_multiplier * std_dev * service_factor
            
            # Recommended stock levels
            minimum_stock = safety_stock
            reorder_point = avg_demand + safety_stock
            maximum_stock = peak_demand + safety_stock
            
            recommendation = {
                "minimum_stock": round(minimum_stock, 2),
                "reorder_point": round(reorder_point, 2),
                "maximum_stock": round(maximum_stock, 2),
                "average_daily_demand": round(avg_demand, 2),
                "peak_demand": round(peak_demand, 2),
                "safety_stock": round(safety_stock, 2),
                "recommendation": f"Maintain stock between {round(minimum_stock)} and {round(maximum_stock)} units. Reorder when stock reaches {round(reorder_point)} units.",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info("Inventory recommendations generated successfully")
            return recommendation
            
        except Exception as e:
            logger.error(f"Error generating inventory recommendations: {str(e)}")
            raise
