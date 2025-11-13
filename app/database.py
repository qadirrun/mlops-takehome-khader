"""Database module for logging predictions."""
import os
from datetime import datetime
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

logger = logging.getLogger(__name__)

# Database connection parameters
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "mlflow_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "mlflow_password")
DB_NAME = os.getenv("DB_NAME", "iris_logs")


def get_db_connection():
    """Get a database connection."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return conn
    except psycopg2.Error as e:
        logger.error(f"Failed to connect to database: {e}")
        return None


def init_db():
    """Initialize database tables."""
    conn = get_db_connection()
    if not conn:
        logger.warning("Could not initialize database - connection failed")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Create predictions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id SERIAL PRIMARY KEY,
                request_id VARCHAR(255) UNIQUE NOT NULL,
                model_name VARCHAR(255) NOT NULL,
                model_version VARCHAR(50) NOT NULL,
                features FLOAT8[] NOT NULL,
                prediction INTEGER NOT NULL,
                probability FLOAT NOT NULL,
                latency_ms FLOAT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create index on request_id and timestamp for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_predictions_request_id 
            ON predictions(request_id);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_predictions_timestamp 
            ON predictions(timestamp);
        """)
        
        conn.commit()
        logger.info("✓ Database initialized successfully")
        return True
    except psycopg2.Error as e:
        logger.error(f"Failed to initialize database: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def log_prediction(
    request_id: str,
    model_name: str,
    model_version: str,
    features: list,
    prediction: int,
    probability: float,
    latency_ms: float,
    timestamp: datetime
) -> bool:
    """Log a prediction to the database."""
    conn = get_db_connection()
    if not conn:
        logger.warning(f"Could not log prediction {request_id} - DB connection failed")
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO predictions 
            (request_id, model_name, model_version, features, prediction, 
             probability, latency_ms, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            request_id,
            model_name,
            model_version,
            features,
            prediction,
            probability,
            latency_ms,
            timestamp
        ))
        conn.commit()
        logger.debug(f"✓ Logged prediction {request_id}")
        return True
    except psycopg2.Error as e:
        logger.error(f"Failed to log prediction {request_id}: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def get_predictions(limit: int = 100) -> list:
    """Get recent predictions from database."""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT * FROM predictions 
            ORDER BY timestamp DESC 
            LIMIT %s
        """, (limit,))
        results = cursor.fetchall()
        return results
    except psycopg2.Error as e:
        logger.error(f"Failed to fetch predictions: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

