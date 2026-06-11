"""
Configuration and utility functions for the application.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


class Config:
    """Application configuration."""
    
    # API Settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    API_WORKERS = int(os.getenv("API_WORKERS", "1"))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # CORS Settings
    ALLOWED_ORIGINS = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:8080"
    ).split(",")
    
    # Firebase Settings
    FIREBASE_CREDENTIALS_PATH = os.getenv(
        "FIREBASE_CREDENTIALS_PATH",
        "./config/firebase-credentials.json"
    )
    FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "")
    FIREBASE_ENABLED = os.getenv("ENABLE_FIREBASE", "true").lower() == "true"
    
    # Model Settings
    MODEL_DIRECTORY = os.getenv("MODEL_DIRECTORY", "./app/models")
    XGBOOST_MODEL_PATH = os.getenv(
        "XGBOOST_MODEL_PATH",
        "./app/models/xgboost_model.pkl"
    )
    RANDOM_FOREST_MODEL_PATH = os.getenv(
        "RANDOM_FOREST_MODEL_PATH",
        "./app/models/random_forest_model.pkl"
    )
    
    # Feature Flags
    ENABLE_ANALYTICS = os.getenv("ENABLE_ANALYTICS", "true").lower() == "true"
    
    @staticmethod
    def get_config():
        """Get configuration dictionary."""
        return {
            "api_host": Config.API_HOST,
            "api_port": Config.API_PORT,
            "debug": Config.DEBUG,
            "allowed_origins": Config.ALLOWED_ORIGINS,
            "firebase_enabled": Config.FIREBASE_ENABLED,
        }


if __name__ == "__main__":
    import json
    print(json.dumps(Config.get_config(), indent=2))
