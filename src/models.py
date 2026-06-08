from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.sql import func
from datetime import datetime
from .database import Base

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True) # e.g., "google_play", "app_store", "csv"
    original_text = Column(Text, nullable=False)
    clean_text = Column(Text, nullable=True)
    rating = Column(Float, nullable=True)
    sentiment_score = Column(Float, nullable=True) # e.g., -1.0 to 1.0 or confidence
    sentiment_label = Column(String, index=True, nullable=True) # "POSITIVE", "NEGATIVE", "NEUTRAL"
    category = Column(String(50))
    is_urgent = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    author = Column(String, nullable=True)
    app_version = Column(String, nullable=True)
    
    # Extra Credit Columns
    status = Column(String(50), default="Open")  # Open, In Progress, Resolved
    assignee = Column(String(100), nullable=True)
    language = Column(String(10), default="en")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, nullable=False)
    severity = Column(String(50), default="HIGH")
    is_resolved = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
