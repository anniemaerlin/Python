"""
Firebase database integration module.
Handles connection and operations with Firebase Firestore.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
import json

# Optional Firebase imports
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logger = None

logger = logging.getLogger(__name__)


class FirebaseDB:
    """Firebase database handler for storing and retrieving pricing data."""
    
    _instance = None
    _db = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one Firebase instance."""
        if cls._instance is None:
            cls._instance = super(FirebaseDB, cls).__new__(cls)
        return cls._instance
    
    @staticmethod
    def initialize():
        """Initialize Firebase connection."""
        if not FIREBASE_AVAILABLE:
            logger.warning("Firebase Admin SDK not installed. Database operations will be disabled.")
            return None
            
        try:
            if not firebase_admin._apps:
                # Check for credentials in environment
                creds_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
                
                if creds_path and os.path.exists(creds_path):
                    cred = credentials.Certificate(creds_path)
                    firebase_admin.initialize_app(cred)
                    logger.info("Firebase initialized with credentials from file")
                else:
                    # Initialize with default credentials
                    firebase_admin.initialize_app()
                    logger.info("Firebase initialized with default credentials")
                
                FirebaseDB._db = firestore.client()
            return FirebaseDB._db
        except Exception as e:
            logger.error(f"Firebase initialization error: {str(e)}")
            return None
    
    @staticmethod
    def get_db():
        """Get Firebase database instance."""
        if not FIREBASE_AVAILABLE:
            return None
        if FirebaseDB._db is None:
            FirebaseDB.initialize()
        return FirebaseDB._db
    
    @staticmethod
    def save_pricing_prediction(product_id: str, prediction_data: Dict[str, Any]) -> bool:
        """
        Save pricing prediction to Firestore.
        
        Args:
            product_id: Product identifier
            prediction_data: Prediction data to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        db = FirebaseDB.get_db()
        if db is None:
            logger.debug("Firebase not available, skipping save")
            return False
            
        try:
            prediction_data['timestamp'] = datetime.utcnow()
            
            doc_ref = db.collection('pricing_predictions').document(product_id)
            doc_ref.set(prediction_data, merge=True)
            
            logger.info(f"Saved pricing prediction for product {product_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving prediction: {str(e)}")
            return False
    
    @staticmethod
    def get_pricing_history(product_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve pricing history for a product.
        
        Args:
            product_id: Product identifier
            limit: Maximum number of records to retrieve
            
        Returns:
            List of pricing records
        """
        db = FirebaseDB.get_db()
        if db is None:
            logger.debug("Firebase not available, returning empty list")
            return []
            
        try:
            docs = (db.collection('pricing_predictions')
                   .where('product_id', '==', product_id)
                   .order_by('timestamp', direction=firestore.Query.DESCENDING)
                   .limit(limit)
                   .stream())
            
            results = []
            for doc in docs:
                data = doc.to_dict()
                results.append(data)
            
            logger.info(f"Retrieved {len(results)} pricing records for product {product_id}")
            return results
        except Exception as e:
            logger.error(f"Error retrieving pricing history: {str(e)}")
            return []
    
    @staticmethod
    def save_demand_forecast(product_id: str, forecast_data: Dict[str, Any]) -> bool:
        """
        Save demand forecast to Firestore.
        
        Args:
            product_id: Product identifier
            forecast_data: Forecast data to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        db = FirebaseDB.get_db()
        if db is None:
            logger.debug("Firebase not available, skipping save")
            return False
            
        try:
            forecast_data['timestamp'] = datetime.utcnow()
            forecast_data['product_id'] = product_id
            
            doc_ref = db.collection('demand_forecasts').document()
            doc_ref.set(forecast_data)
            
            logger.info(f"Saved demand forecast for product {product_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving forecast: {str(e)}")
            return False
    
    @staticmethod
    def save_competitor_analysis(product_id: str, analysis_data: Dict[str, Any]) -> bool:
        """
        Save competitor analysis to Firestore.
        
        Args:
            product_id: Product identifier
            analysis_data: Analysis data to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        db = FirebaseDB.get_db()
        if db is None:
            logger.debug("Firebase not available, skipping save")
            return False
            
        try:
            analysis_data['timestamp'] = datetime.utcnow()
            analysis_data['product_id'] = product_id
            
            doc_ref = db.collection('competitor_analysis').document(product_id)
            doc_ref.set(analysis_data, merge=True)
            
            logger.info(f"Saved competitor analysis for product {product_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving competitor analysis: {str(e)}")
            return False
    
    @staticmethod
    def save_customer_segment(customer_id: str, segment_data: Dict[str, Any]) -> bool:
        """
        Save customer segment classification to Firestore.
        
        Args:
            customer_id: Customer identifier
            segment_data: Segment data to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        db = FirebaseDB.get_db()
        if db is None:
            logger.debug("Firebase not available, skipping save")
            return False
            
        try:
            segment_data['timestamp'] = datetime.utcnow()
            
            doc_ref = db.collection('customer_segments').document(customer_id)
            doc_ref.set(segment_data, merge=True)
            
            logger.info(f"Saved segment for customer {customer_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving customer segment: {str(e)}")
            return False
    
    @staticmethod
    def get_customer_data(customer_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve customer data from Firestore.
        
        Args:
            customer_id: Customer identifier
            
        Returns:
            Customer data or None if not found
        """
        db = FirebaseDB.get_db()
        if db is None:
            logger.debug("Firebase not available, returning None")
            return None
            
        try:
            doc = db.collection('customers').document(customer_id).get()
            
            if doc.exists:
                logger.info(f"Retrieved customer data for {customer_id}")
                return doc.to_dict()
            else:
                logger.warning(f"Customer {customer_id} not found")
                return None
        except Exception as e:
            logger.error(f"Error retrieving customer data: {str(e)}")
            return None
    
    @staticmethod
    def save_analytics_event(event_name: str, event_data: Dict[str, Any]) -> bool:
        """
        Save analytics event to Firestore.
        
        Args:
            event_name: Name of the event
            event_data: Event data to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        db = FirebaseDB.get_db()
        if db is None:
            logger.debug("Firebase not available, skipping save")
            return False
            
        try:
            event_data['timestamp'] = datetime.utcnow()
            event_data['event_name'] = event_name
            
            doc_ref = db.collection('analytics_events').document()
            doc_ref.set(event_data)
            
            logger.info(f"Saved analytics event: {event_name}")
            return True
        except Exception as e:
            logger.error(f"Error saving analytics event: {str(e)}")
            return False
