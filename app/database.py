"""Database module for logging predictions."""
import os
import sqlite3
import json
from datetime import datetime
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

logger = logging.getLogger(__name__)

# --- Database Configuration ---
# Use a simple SQLite database for dev/CI, and PostgreSQL for prod
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")

if ENVIRONMENT != "prod":
    DB_DRIVER = "sqlite"
    # Use a file-based SQLite DB in a writable location
    SQLITE_PATH = "/tmp/predictions.db"
else:
    DB_DRIVER = "postgres"
    DB_HOST = os.getenv("DB_HOST", "postgres")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))
    DB_USER = os.getenv("DB_USER", "mlflow_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "mlflow_password")
    DB_NAME = os.getenv("DB_NAME", "iris_logs")


def get_db_connection():
    """Get a database connection based on the configured driver."""
    if DB_DRIVER == "sqlite":
        try:
            conn = sqlite3.connect(SQLITE_PATH)
            # Return rows as dictionary-like objects
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to SQLite database: {e}")
            return None

    elif DB_DRIVER == "postgres":
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

    else:
        logger.error(f"Unsupported DB_DRIVER: {DB_DRIVER}")
        return None


def init_db():
    """Initialize database tables with driver-specific syntax."""
    conn = get_db_connection()
    if not conn:
        logger.warning("Could not initialize database - connection failed")
        return False

    try:
        cursor = conn.cursor()

        # --- Get driver-specific table creation SQL ---
        if DB_DRIVER == "sqlite":
            # SQLite uses TEXT for JSON and INTEGER PRIMARY KEY for auto-increment
            create_table_sql = """
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT UNIQUE NOT NULL,
                    model_name TEXT NOT NULL,
                    model_version TEXT NOT NULL,
                    features TEXT NOT NULL,  -- Store as JSON string
                    prediction INTEGER NOT NULL,
                    probability REAL NOT NULL,
                    latency_ms REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
            """
        else: # postgres
            create_table_sql = """
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
            """

        cursor.execute(create_table_sql)

        # --- Create indexes (syntax is compatible) ---
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_request_id ON predictions(request_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON predictions(timestamp);")

        conn.commit()
        logger.info(f"✓ Database ({DB_DRIVER}) initialized successfully")
        return True
    except (psycopg2.Error, sqlite3.Error) as e:
        logger.error(f"Failed to initialize database: {e}")
        conn.rollback()
        return False
    finally:
        if conn:
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
    """Log a prediction to the database, handling different DB drivers."""
    conn = get_db_connection()
    if not conn:
        logger.warning(f"Could not log prediction {request_id} - DB connection failed")
        return False

    try:
        cursor = conn.cursor()

        # Adapt for different drivers
        if DB_DRIVER == "sqlite":
            sql = """
                INSERT INTO predictions
                (request_id, model_name, model_version, features, prediction,
                 probability, latency_ms, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            # Serialize list to JSON string for SQLite
            params = (
                request_id, model_name, model_version, json.dumps(features),
                prediction, probability, latency_ms, timestamp
            )
        else: # postgres
            sql = """
                INSERT INTO predictions
                (request_id, model_name, model_version, features, prediction,
                 probability, latency_ms, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                request_id, model_name, model_version, features,
                prediction, probability, latency_ms, timestamp
            )

        cursor.execute(sql, params)
        conn.commit()
        logger.debug(f"✓ Logged prediction {request_id}")
        return True
    except (psycopg2.Error, sqlite3.Error) as e:
        logger.error(f"Failed to log prediction {request_id}: {e}")
        conn.rollback()
        return False
    finally:
        if conn:
            cursor.close()
            conn.close()


def get_predictions(limit: int = 100) -> list:
    """Get recent predictions from the database."""
    conn = get_db_connection()
    if not conn:
        return []

    try:
        if DB_DRIVER == "postgres":
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            sql = "SELECT * FROM predictions ORDER BY timestamp DESC LIMIT %s"
            params = (limit,)
        else: # sqlite
            cursor = conn.cursor()
            sql = "SELECT * FROM predictions ORDER BY timestamp DESC LIMIT ?"
            params = (limit,)

        cursor.execute(sql, params)
        results = cursor.fetchall()

        # Convert to list of dicts and deserialize features if SQLite
        final_results = []
        for row in results:
            row_dict = dict(row)
            if DB_DRIVER == "sqlite" and 'features' in row_dict:
                row_dict['features'] = json.loads(row_dict['features'])
            final_results.append(row_dict)

        return final_results

    except (psycopg2.Error, sqlite3.Error) as e:
        logger.error(f"Failed to fetch predictions: {e}")
        return []
    finally:
        if conn:
            cursor.close()
            conn.close()

