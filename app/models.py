from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ARRAY
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

# Define the base class for declarative models
Base = declarative_base()

# Define the Predictions table model
class Prediction(Base):
    __tablename__ = 'predictions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(String(255), unique=True, nullable=False, index=True)
    model_name = Column(String(255), nullable=False)
    model_version = Column(String(50), nullable=False)
    
    # Use ARRAY(Float) for PostgreSQL, which is our primary target for migrations
    features = Column(ARRAY(Float), nullable=False)
    prediction = Column(Integer, nullable=False)
    probability = Column(Float, nullable=False)
    latency_ms = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())

