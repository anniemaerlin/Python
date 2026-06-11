"""
Main FastAPI application module.
Entry point for the Dynamic Pricing Engine backend.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import logging.handlers
import os
from datetime import datetime
import sys

# Import routes
from app.routes import pricing, forecast, customer, competitor, chat
from app.services.pricing_service import PricingService
from app.database.firebase import FirebaseDB

# Configure logging
def setup_logging():
    """Configure application logging."""
    log_level = os.getenv("LOG_LEVEL", "INFO")
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        "logs/app.log",
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(getattr(logging, log_level))
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("=" * 50)
    logger.info("Starting Dynamic Pricing Engine Backend")
    logger.info("=" * 50)
    
    try:
        # Load ML models
        logger.info("Loading ML models...")
        if PricingService.load_models():
            logger.info("ML models loaded successfully")
        else:
            logger.warning("Failed to load ML models, running in degraded mode")
        
        # Initialize Firebase
        logger.info("Initializing Firebase connection...")
        try:
            FirebaseDB.initialize()
            logger.info("Firebase initialized successfully")
        except Exception as e:
            logger.warning(f"Firebase initialization failed: {str(e)}")
            logger.info("Continuing without Firebase - analytics features disabled")
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("=" * 50)
    logger.info("Shutting down Dynamic Pricing Engine Backend")
    logger.info("=" * 50)
    logger.info("Application shutdown completed")


# Create FastAPI application
app = FastAPI(
    title="Dynamic Pricing Engine API",
    description="Machine Learning based Dynamic Pricing System with Demand Forecasting and Competitor Analysis",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS — allow all localhost ports and file:// origins for frontend dev
_env_origins = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [o.strip() for o in _env_origins.split(",") if o.strip()] if _env_origins else []

# Always include common dev origins
_dev_origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5500",
    "http://localhost:8080",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:8080",
    "null",   # file:// origin appears as "null"
]
for o in _dev_origins:
    if o not in allowed_origins:
        allowed_origins.append(o)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"http://localhost:\d+",  # allow any localhost port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc) if os.getenv("DEBUG", "false").lower() == "true" else "An error occurred",
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url)
        }
    )


# Include routers
app.include_router(pricing.router)
app.include_router(forecast.router)
app.include_router(customer.router)
app.include_router(competitor.router)
app.include_router(chat.router)


@app.get(
    "/",
    tags=["Health"],
    summary="Root Endpoint",
    description="Welcome to Dynamic Pricing Engine API"
)
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Dynamic Pricing Engine",
        "version": "1.0.0",
        "description": "ML-based dynamic pricing system with forecasting and competitor analysis",
        "endpoints": {
            "pricing": "/api/v1/pricing",
            "forecast": "/api/v1/forecast",
            "customer": "/api/v1/customer",
            "competitor": "/api/v1/competitor",
            "chat": "/api/v1/chat",
            "docs": "/api/docs",
            "redoc": "/api/redoc"
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get(
    "/api/health",
    tags=["Health"],
    summary="Overall Health Check",
    description="Check the health of all services"
)
async def health_check():
    """
    Overall health check endpoint.
    Returns status of all services.
    """
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "pricing": "operational",
                "forecast": "operational",
                "customer": "operational",
                "competitor": "operational",
                "chat": "operational",
                "models": "loaded" if PricingService.are_models_loaded() else "not_loaded"
            },
            "api_version": "1.0.0"
        }
        
        logger.info("Health check passed")
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


@app.get(
    "/api/info",
    tags=["Info"],
    summary="API Information",
    description="Get detailed API information"
)
async def api_info():
    """Get detailed API information."""
    return {
        "service": "Dynamic Pricing Engine Backend",
        "version": "1.0.0",
        "features": [
            "Dynamic price prediction",
            "Demand forecasting",
            "Competitor price tracking",
            "Customer segmentation",
            "Revenue impact simulation",
            "Explainable AI"
        ],
        "ml_models": [
            "XGBoost Regressor",
            "Random Forest Regressor"
        ],
        "database": "Firebase Firestore",
        "framework": "FastAPI",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    workers = int(os.getenv("API_WORKERS", "1"))
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Workers: {workers}")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        workers=workers if not debug else 1,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
