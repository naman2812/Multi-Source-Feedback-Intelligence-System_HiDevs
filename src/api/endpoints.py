from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Feedback, Alert
from ..schemas import FeedbackResponse, FeedbackCreate, AlertResponse
from ..processing.analyzer import analyze_sentiment
from ..ingestion.api_clients import fetch_google_play_reviews
from ..actions.reports import generate_weekly_report
from ..worker import process_feedback_task, ingest_playstore_task, ingest_appstore_task
from ..intelligence.ai_prompts import generate_suggested_response
from fastapi.responses import FileResponse
import os
from datetime import datetime, timedelta
import math

router = APIRouter()

@router.post("/feedback", response_model=FeedbackResponse)
def create_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    """Ingest a single feedback item and process it synchronously."""
    # 1. Analyze Sentiment
    sentiment_result = analyze_sentiment(feedback.original_text)
    
    # 2. Categorize (Basic heuristic)
    category = "general"
    lower_text = feedback.original_text.lower()
    if "bug" in lower_text or "crash" in lower_text or "broken" in lower_text:
        category = "bug"
    elif "feature" in lower_text or "add" in lower_text or "please" in lower_text:
        category = "feature_request"

    # 3. Determine Urgency
    is_urgent = sentiment_result["label"] == "NEGATIVE" and category == "bug"

    # 4. Save to Database
    db_feedback = Feedback(
        source=feedback.source,
        original_text=feedback.original_text,
        rating=feedback.rating,
        author=feedback.author,
        app_version=feedback.app_version,
        sentiment_score=sentiment_result["score"],
        sentiment_label=sentiment_result["label"],
        category=category,
        is_urgent=is_urgent
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

@router.get("/feedback", response_model=List[FeedbackResponse])
def get_all_feedback(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve all feedback with pagination."""
    feedbacks = db.query(Feedback).order_by(Feedback.timestamp.desc()).offset(skip).limit(limit).all()
    return feedbacks

@router.get("/feedback/{feedback_id}/suggest-response")
def suggest_response(feedback_id: int, db: Session = Depends(get_db)):
    """Generate an AI-suggested response for a specific feedback item."""
    fb = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not fb:
        raise HTTPException(status_code=404, detail="Feedback not found")
        
    suggestion = generate_suggested_response(fb.original_text, fb.sentiment_label, fb.category, fb.language)
    return {"suggested_reply": suggestion}

@router.put("/feedback/{feedback_id}/status")
def update_feedback_status(feedback_id: int, status: str, assignee: str = None, db: Session = Depends(get_db)):
    """Update status and assignee (Team Collaboration feature)."""
    fb = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not fb:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    fb.status = status
    if assignee:
        fb.assignee = assignee
        
    db.commit()
    db.refresh(fb)
    return fb

@router.get("/alerts", response_model=List[AlertResponse])
def get_alerts(db: Session = Depends(get_db)):
    """Retrieve all active system alerts."""
    return db.query(Alert).filter(Alert.is_resolved == False).order_by(Alert.timestamp.desc()).limit(20).all()

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Get high-level statistics for the dashboard."""
    total = db.query(Feedback).count()
    positive = db.query(Feedback).filter(Feedback.sentiment_label == "POSITIVE").count()
    negative = db.query(Feedback).filter(Feedback.sentiment_label == "NEGATIVE").count()
    neutral = db.query(Feedback).filter(Feedback.sentiment_label == "NEUTRAL").count()
    bugs = db.query(Feedback).filter(Feedback.category == "bug").count()
    
    # Calculate 7-day historical trend for the line chart
    trend_data = []
    end_date = datetime.utcnow()
    for i in range(6, -1, -1):
        target_date = end_date - timedelta(days=i)
        day_str = target_date.strftime("%a") # e.g. "Mon"
        
        # count for this specific day
        pos = db.query(Feedback).filter(
            Feedback.sentiment_label == "POSITIVE",
            Feedback.timestamp >= target_date.replace(hour=0, minute=0, second=0),
            Feedback.timestamp <= target_date.replace(hour=23, minute=59, second=59)
        ).count()
        
        neg = db.query(Feedback).filter(
            Feedback.sentiment_label == "NEGATIVE",
            Feedback.timestamp >= target_date.replace(hour=0, minute=0, second=0),
            Feedback.timestamp <= target_date.replace(hour=23, minute=59, second=59)
        ).count()
        
        neu = db.query(Feedback).filter(
            Feedback.sentiment_label == "NEUTRAL",
            Feedback.timestamp >= target_date.replace(hour=0, minute=0, second=0),
            Feedback.timestamp <= target_date.replace(hour=23, minute=59, second=59)
        ).count()
        
        trend_data.append({
            "name": day_str,
            "positive": pos,
            "negative": neg,
            "neutral": neu
        })
    
    return {
        "total_feedback": total,
        "sentiment_distribution": {
            "positive": positive,
            "negative": negative,
            "neutral": neutral
        },
        "total_bugs": bugs,
        "trend_data": trend_data
    }

@router.get("/forecast")
def get_forecast(db: Session = Depends(get_db)):
    """Use Linear Regression to forecast sentiment for the next 3 days based on the past 7 days."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    
    # Fetch data points
    recent_feedbacks = db.query(Feedback.timestamp, Feedback.sentiment_score).filter(
        Feedback.timestamp >= start_date,
        Feedback.sentiment_score != None
    ).order_by(Feedback.timestamp).all()
    
    if len(recent_feedbacks) < 10:
        return {"forecast": [], "message": "Not enough data for forecasting."}
        
    # Prepare data for pure Python linear regression
    n = len(recent_feedbacks)
    base_time = start_date.timestamp()
    
    x_sum = 0
    y_sum = 0
    xx_sum = 0
    xy_sum = 0
    
    for timestamp, score in recent_feedbacks:
        x = (timestamp.timestamp() - base_time) / (24 * 3600)
        y = score
        x_sum += x
        y_sum += y
        xx_sum += x * x
        xy_sum += x * y
        
    # Calculate slope (m) and intercept (b)
    denominator = (n * xx_sum - x_sum * x_sum)
    if denominator == 0:
        m = 0
        b = y_sum / n
    else:
        m = (n * xy_sum - x_sum * y_sum) / denominator
        b = (y_sum - m * x_sum) / n
    
    # Predict next 3 days
    forecast = []
    for i in range(1, 4):
        future_day = 7 + i
        predicted_score = m * future_day + b
        predicted_score = max(min(predicted_score, 1.0), -1.0)
        future_date = end_date + timedelta(days=i)
        
        forecast.append({
            "date": future_date.strftime("%Y-%m-%d"),
            "predicted_score": round(predicted_score, 2),
            "trend": "Up" if m > 0 else "Down"
        })
        
    return {"forecast": forecast}

@router.post("/ingest/playstore")
def ingest_playstore(app_id: str = "com.spotify.music", count: int = 20):
    """Trigger background task to fetch reviews from Play Store and save to DB."""
    # Spawn a Celery background task
    ingest_playstore_task.delay(app_id, count)
    return {"status": "accepted", "message": f"Ingestion task started for {app_id} in the background."}

@router.post("/ingest/appstore")
def ingest_appstore(app_name: str = "spotify-music-and-podcasts", app_id: int = 324684580, count: int = 20):
    """Trigger background task to fetch reviews from App Store and save to DB."""
    ingest_appstore_task.delay(app_name, app_id, count)
    return {"status": "accepted", "message": f"Ingestion task started for {app_name} in the background."}

@router.get("/report/download")
def download_report(db: Session = Depends(get_db)):
    """Generate and download a weekly PDF report."""
    stats = get_stats(db)
    
    # Get top 5 most recent urgent issues
    top_issues_query = db.query(Feedback).filter(Feedback.is_urgent == True).order_by(Feedback.timestamp.desc()).limit(5).all()
    top_issues = [{"source": fb.source, "original_text": fb.original_text} for fb in top_issues_query]
    
    report_path = generate_weekly_report(stats, top_issues, "weekly_report.pdf")
    
    if os.path.exists(report_path):
        return FileResponse(path=report_path, filename="Weekly_Feedback_Report.pdf", media_type='application/pdf')
    raise HTTPException(status_code=500, detail="Could not generate report")
