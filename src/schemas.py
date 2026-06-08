from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class FeedbackBase(BaseModel):
    source: str
    original_text: str
    rating: Optional[float] = None
    author: Optional[str] = None
    app_version: Optional[str] = None

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackResponse(FeedbackBase):
    id: int
    clean_text: Optional[str] = None
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    category: Optional[str] = None
    is_urgent: Optional[bool] = False
    
    # Extra Credit
    status: Optional[str] = "Open"
    assignee: Optional[str] = None
    language: Optional[str] = "en"
    timestamp: datetime

    class Config:
        from_attributes = True # updated for Pydantic v2

class TrendStats(BaseModel):
    date: str
    positive: int
    negative: int
    neutral: int

class AlertResponse(BaseModel):
    id: int
    message: str
    severity: str
    is_resolved: bool
    timestamp: datetime
    
    class Config:
        from_attributes = True
