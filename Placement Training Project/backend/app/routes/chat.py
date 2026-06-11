"""
AI Chat Assistant routes module.
Provides intelligent chatbot responses using backend pricing knowledge.
"""

from fastapi import APIRouter, HTTPException, Body
import logging
import re
from typing import Dict, Any
from datetime import datetime

from app.services.pricing_service import PricingService
from app.services.forecast_service import ForecastService
from app.services.segmentation_service import SegmentationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chat", tags=["AI Chat Assistant"])


# ─────────────────────────────────────────────
#  Static knowledge base
# ─────────────────────────────────────────────
KB = {
    "greet": (
        "Hello! I'm **PriceIQ**, your AI pricing assistant. I can help you with:\n\n"
        "• Price predictions & optimization\n"
        "• Demand forecasting\n"
        "• Competitor analysis\n"
        "• Customer segmentation\n"
        "• Revenue simulation\n\n"
        "What would you like to explore?"
    ),
    "help": (
        "**I can help you with:**\n\n"
        "• `predict price` — Get AI price recommendation\n"
        "• `forecast demand` — See demand trend analysis\n"
        "• `analyze competitors` — Check market positioning\n"
        "• `segment customer` — Classify a customer profile\n"
        "• `simulate revenue` — Revenue impact calculator\n"
        "• `what is dynamic pricing?` — Learn concepts\n"
        "• `pricing tips` — Best practices\n\n"
        "Or just ask me anything in plain English!"
    ),
    "about": (
        "**PP.PRICING** is an enterprise-grade AI Dynamic Pricing Engine that uses:\n\n"
        "• **XGBoost & Random Forest** ML models trained on real pricing data\n"
        "• **Real-time competitor monitoring** across Amazon, Flipkart, Meesho & more\n"
        "• **Demand forecasting** with seasonal pattern detection\n"
        "• **Customer segmentation** — VIP, Regular, Budget-Conscious & more\n"
        "• **Revenue impact simulation** with price elasticity modeling"
    ),
    "dynamic_pricing": (
        "**Dynamic Pricing** is a strategy where prices adjust in real-time based on:\n\n"
        "• **Demand** — High demand → higher price opportunity\n"
        "• **Competition** — Monitor and respond to competitor prices\n"
        "• **Inventory** — Low stock signals scarcity pricing\n"
        "• **Conversion Rate** — Optimize for maximum revenue\n"
        "• **Promotions** — Factor in active discounts\n\n"
        "Our ML models analyze all these signals to recommend the optimal price instantly."
    ),
    "tips": (
        "**Pricing Best Practices:**\n\n"
        "• Monitor competitors daily — prices change fast\n"
        "• Use demand forecasting to anticipate high-traffic periods\n"
        "• VIP customers need less discount (5%) vs Budget-Conscious (15%)\n"
        "• Inventory below safety margin = time to increase price\n"
        "• A 10% price increase with elastic demand can increase revenue by 8–12%\n"
        "• Confidence score above 85% = act on the recommendation immediately"
    ),
    "confidence": (
        "The **Confidence Score** measures how reliable our ML prediction is:\n\n"
        "• 90–100% — Very High — Act immediately\n"
        "• 75–89% — High — Recommended action\n"
        "• 60–74% — Moderate — Review before acting\n"
        "• <60% — Low — Gather more data first\n\n"
        "Confidence is based on data quality, price reasonableness, and model agreement."
    ),
    "segments": (
        "**Customer Segments:**\n\n"
        "• **VIP** — High LTV, loyal, 5% discount max, 95% retention\n"
        "• **Regular** — Consistent buyers, 3% discount, 75% retention\n"
        "• **Budget-Conscious** — Price-sensitive, needs 15% discount\n"
        "• **Inactive** — 90+ days inactive, re-engage with 20% offer\n"
        "• **New** — Acquisition phase, 10% welcome discount\n\n"
        "Customer segment determines the optimal discount and pricing strategy."
    ),
    "revenue": (
        "Revenue impact is calculated as:\n\n"
        "`Revenue = Demand × Price`\n"
        "`Demand = Base × (1 − Elasticity × ΔPrice%)`\n\n"
        "• **Price Elasticity** measures how sensitive demand is to price changes\n"
        "• Higher elasticity = bigger demand drop when you raise price\n"
        "• Our simulator shows real-time revenue & profit projections\n"
        "• Try the **Revenue Impact Simulator** on the dashboard!"
    ),
    "forecast": (
        "Demand forecasting uses **time-series analysis** with:\n\n"
        "• Linear trend detection (slope calculation)\n"
        "• Seasonal pattern recognition (weekly/monthly)\n"
        "• Confidence intervals (±12% by default)\n"
        "• 1 to 365 day forecast horizon\n\n"
        "Prediction accuracy is typically **85–98%** depending on data quality."
    ),
    "competitor": (
        "**Competitor Intelligence** monitors:\n\n"
        "• Real-time price positions vs Amazon, Flipkart, Meesho, Reliance Digital\n"
        "• Market share potential based on your positioning\n"
        "• Recommended action: maintain, increase, or reduce price\n"
        "• Competitive strategy: Budget Leader, Value Player, Premium Standard\n\n"
        "Being 5–10% below market typically yields +5 to +15% market share gain."
    ),
    "models": (
        "**ML Models Used:**\n\n"
        "• **XGBoost** — Gradient boosted trees, best for structured pricing data, fast inference\n"
        "• **Random Forest** — Ensemble of decision trees, robust to outliers\n\n"
        "Both models use 8 features: current price, competitor price, demand, inventory, "
        "conversion rate, promotion flag, discount %, and demand index.\n\n"
        "Use XGBoost for speed; Random Forest for stability."
    ),
    "inventory": (
        "**Inventory Management Tips:**\n\n"
        "• Safety Stock = Avg Daily Demand × Safety Multiplier (1.5×)\n"
        "• Reorder Point = (Avg Demand × Lead Time) + Safety Stock\n"
        "• Low inventory (<30 units) → price increase signal\n"
        "• Overstocked (>200 units) → consider discount/promotion\n\n"
        "Use the **Demand Forecast** page to get inventory recommendations."
    ),
    "elasticity": (
        "**Price Elasticity of Demand:**\n\n"
        "• Elasticity = % Change in Demand / % Change in Price\n"
        "• **Elastic** (>1): Demand drops more than price rises — careful with increases\n"
        "• **Inelastic** (<1): Demand stays stable — can safely raise price\n"
        "• **Unit elastic** (=1): Revenue stays constant at any price change\n\n"
        "VIP customers: elasticity -0.5 (inelastic)\n"
        "Budget-Conscious customers: elasticity -2.0 (highly elastic)"
    ),
    "xgboost": (
        "**XGBoost (Extreme Gradient Boosting):**\n\n"
        "• Builds decision trees sequentially, each correcting the previous\n"
        "• Extremely fast inference — ideal for real-time pricing\n"
        "• Handles missing data natively\n"
        "• Typically 2–5% more accurate than Random Forest on tabular data\n\n"
        "This is the **default model** in PP.PRICING for price prediction."
    ),
    "random_forest": (
        "**Random Forest:**\n\n"
        "• Builds hundreds of independent decision trees, averages results\n"
        "• More robust to outliers than XGBoost\n"
        "• Better when training data is noisy or limited\n"
        "• Provides natural feature importance scores\n\n"
        "Use it as a **secondary validation** alongside XGBoost."
    ),
}


# ─────────────────────────────────────────────
#  Intent detection
# ─────────────────────────────────────────────
def detect_intent(msg: str) -> str:
    m = msg.lower().strip()

    patterns = [
        ("greet",           r"^(hello|hi|hey|good morning|good afternoon|greet|howdy|sup|what's up)"),
        ("help",            r"help|what can you|what do you|commands|features|show me"),
        ("about",           r"about|what is pp|what is this|who are you|what are you"),
        ("dynamic_pricing", r"dynamic pricing|how does pricing work|price strategy|pricing model|what is pricing"),
        ("tips",            r"tip|best practice|advice|suggest|recommendation"),
        ("confidence",      r"confidence|score|reliable|accuracy|trust|how sure"),
        ("segments",        r"segment|vip|regular|budget.conscious|inactive|new customer|customer type|customer class"),
        ("revenue",         r"revenue|profit|elasticity|simulate|simulator|revenue impact"),
        ("api_price",       r"predict price|price predict|recommend price|optimal price|best price|get price|what should.*price|how much.*charge"),
        ("api_competitor",  r"analyze competitor|competitor price|compare price|check competition|market analysis"),
        ("api_segment",     r"classify.*customer|which segment|customer segment|identify segment|classify customer"),
        ("api_forecast",    r"run forecast|demand forecast|forecast demand|show.*demand|trend.*demand"),
        ("forecast",        r"forecast|predict demand|future demand|demand predict|demand trend"),
        ("competitor",      r"competitor|market intel|amazon|flipkart|meesho|reliance|market share"),
        ("models",          r"model|xgboost|random forest|ml model|machine learning|algorithm|which model"),
        ("inventory",       r"inventory|stock|reorder|warehouse|supply|understocked|overstocked"),
        ("elasticity",      r"elasticity|elastic|inelastic|price sensitive|demand change"),
        ("xgboost",         r"\bxgboost\b|gradient boost|gbm"),
        ("random_forest",   r"random forest|bagging|ensemble"),
    ]

    for intent, pattern in patterns:
        if re.search(pattern, m):
            return intent

    return "unknown"


# ─────────────────────────────────────────────
#  Live API helpers
# ─────────────────────────────────────────────
def _live_price() -> str:
    sample = {
        "current_price": 1200, "competitor_price": 1280, "demand": 200,
        "inventory": 50, "conversion_rate": 0.12, "promotion": 1,
        "discount_percent": 0, "demand_index": 0.75
    }
    result = PricingService.predict_price(sample, "xgboost")
    sign = "+" if result["price_change_percent"] >= 0 else ""
    conf_label = "Very High" if result["confidence_score"] >= 90 else "High" if result["confidence_score"] >= 75 else "Moderate"
    return (
        f"**Live Price Prediction** (XGBoost)\n\n"
        f"• Recommended Price: `₹{round(result['recommended_price']):,}`\n"
        f"• Price Change: `{sign}{result['price_change_percent']:.1f}%`\n"
        f"• Confidence: `{result['confidence_score']:.0f}%` ({conf_label})\n"
        f"• Model: `{result['model_used']}`\n"
        f"• Revenue Impact: `₹{abs(result['revenue_impact']):,.0f}`\n\n"
        f"*Based on sample product: ₹1200 current, ₹1280 competitor, 200 units demand.*"
    )


def _live_forecast() -> str:
    hist = [50, 55, 53, 60, 65, 70, 68, 72, 75, 78, 80, 82]
    result = ForecastService.forecast_demand(hist, days_ahead=7, seasonality="weekly")
    avg = sum(result["forecasted_demand"]) / len(result["forecasted_demand"])
    preview = ", ".join(str(round(v)) for v in result["forecasted_demand"][:5])
    trend_map = {"high": "📈 HIGH", "low": "📉 LOW", "medium": "➡️ STABLE"}
    trend_label = trend_map.get(result["trend"], "➡️ STABLE")
    return (
        f"**7-Day Demand Forecast**\n\n"
        f"• Trend: `{trend_label}`\n"
        f"• Prediction Accuracy: `{result['prediction_accuracy']:.1f}%`\n"
        f"• Avg Forecasted Demand: `{avg:.0f} units/day`\n"
        f"• Next 5 Days: `{preview}…`\n\n"
        f"Go to the **Demand Forecast** page for the full interactive chart!"
    )


def _live_segment() -> str:
    sample = {
        "purchase_frequency": 12, "average_order_value": 1200,
        "customer_lifetime_value": 14400, "loyalty_score": 0.85,
        "days_since_purchase": 5
    }
    result = SegmentationService.segment_customer(sample)
    strategy = result.get("personalized_pricing_strategy", {})
    actions = strategy.get("recommended_actions", [])[:3] if isinstance(strategy, dict) else []
    action_list = "\n".join(f"  • {a}" for a in actions) if actions else ""
    return (
        f"**Customer Segmentation** (sample profile)\n\n"
        f"• Segment: `{result['segment'].replace('_', ' ')}`\n"
        f"• Description: {result['segment_description']}\n"
        f"• Recommended Discount: `{result['recommended_discount']}%`\n"
        f"• Retention Probability: `{result['retention_probability'] * 100:.0f}%`\n"
        f"• Price Elasticity: `{result['recommended_price_elasticity']}`\n"
        + (f"\n**Recommended Actions:**\n{action_list}" if action_list else "")
    )


def _live_competitor() -> str:
    from statistics import mean
    prices = {"Amazon": 1280, "Flipkart": 1320, "Meesho": 1180, "Reliance Digital": 1300}
    avg_price = mean(prices.values())
    your_price = 1200
    diff_pct = (your_price - avg_price) / avg_price * 100
    position = "below" if diff_pct < 0 else "above" if diff_pct > 0 else "at"
    breakdown = "\n".join(f"  • {n}: `₹{p:,}`" for n, p in prices.items())
    return (
        f"**Competitor Analysis**\n\n"
        f"• Your Price: `₹{your_price:,}`\n"
        f"• Avg Market Price: `₹{avg_price:,.0f}`\n"
        f"• Your Position: `{position.upper()}` market by `{abs(diff_pct):.1f}%`\n\n"
        f"**Market Breakdown:**\n{breakdown}\n\n"
        f"*You are positioned below average — good market share opportunity!*"
    )


# ─────────────────────────────────────────────
#  Core response engine
# ─────────────────────────────────────────────
def generate_response(message: str) -> Dict[str, Any]:
    """Generate a response for a given user message."""
    intent = detect_intent(message)

    # Static KB intents
    kb_intents = [
        "greet", "help", "about", "dynamic_pricing", "tips", "confidence",
        "segments", "revenue", "forecast", "competitor", "models",
        "inventory", "elasticity", "xgboost", "random_forest"
    ]

    if intent in kb_intents:
        return {"reply": KB[intent], "intent": intent, "source": "knowledge_base"}

    # Live API intents
    try:
        if intent == "api_price":
            return {"reply": _live_price(), "intent": intent, "source": "live_api"}
        if intent == "api_competitor":
            return {"reply": _live_competitor(), "intent": intent, "source": "live_api"}
        if intent == "api_segment":
            return {"reply": _live_segment(), "intent": intent, "source": "live_api"}
        if intent == "api_forecast":
            return {"reply": _live_forecast(), "intent": intent, "source": "live_api"}
    except Exception as e:
        logger.error(f"Live API call failed for intent {intent}: {e}")
        # Fall back to KB equivalent
        fallback_map = {
            "api_price": "dynamic_pricing",
            "api_competitor": "competitor",
            "api_segment": "segments",
            "api_forecast": "forecast",
        }
        return {
            "reply": KB.get(fallback_map.get(intent, "help"),
                            "Sorry, I couldn't fetch live data right now. Please check the backend is running."),
            "intent": intent,
            "source": "fallback"
        }

    # Unknown — helpful suggestions
    unknown_replies = [
        (
            "Hmm, I'm not sure about that specific topic. Try asking me:\n\n"
            "• `predict price` — AI price recommendation\n"
            "• `forecast demand` — Demand trend analysis\n"
            "• `analyze competitors` — Market positioning\n"
            "• `pricing tips` — Best practices\n"
            "• `what is dynamic pricing?` — Learn the concept"
        ),
        (
            "I'm specialized in pricing intelligence. You can ask me about:\n\n"
            "• Dynamic pricing strategies\n"
            "• Demand forecasting\n"
            "• Customer segmentation\n"
            "• Competitor analysis\n"
            "• ML model explanations\n\n"
            "Type `help` to see all available commands."
        ),
    ]
    import random
    return {
        "reply": random.choice(unknown_replies),
        "intent": "unknown",
        "source": "fallback"
    }


# ─────────────────────────────────────────────
#  Route
# ─────────────────────────────────────────────
@router.post(
    "/message",
    summary="Send a message to the AI chatbot",
    description="Send a natural language message and get an AI-powered pricing response"
)
async def chat_message(
    payload: Dict[str, Any] = Body(
        ...,
        example={"message": "predict price", "session_id": "user123"}
    )
):
    """
    Chat with PriceIQ — the AI pricing assistant.

    - **message**: Natural language question or command
    - **session_id**: Optional session identifier for logging

    Returns:
    - reply: Markdown-formatted response
    - intent: Detected intent
    - source: knowledge_base | live_api | fallback
    """
    try:
        message = payload.get("message", "").strip()
        if not message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        if len(message) > 500:
            raise HTTPException(status_code=400, detail="Message too long (max 500 characters)")

        logger.info(f"Chat message received: {message[:80]!r}")
        result = generate_response(message)
        result["timestamp"] = datetime.utcnow().isoformat()

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat service error: {str(e)}")


@router.get(
    "/health",
    summary="Chat service health check"
)
async def chat_health():
    return {
        "status": "healthy",
        "service": "chat",
        "timestamp": datetime.utcnow().isoformat()
    }
