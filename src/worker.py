from celery import Celery
import os
from .database import SessionLocal
from .models import Feedback, Alert
from .processing.analyzer import analyze_sentiment
from .ingestion.api_clients import fetch_google_play_reviews, fetch_app_store_reviews
import logging

logger = logging.getLogger(__name__)

# Configure Celery
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery(
    "worker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

# Force synchronous execution locally since Redis/Docker is not installed on this host
celery_app.conf.task_always_eager = True

@celery_app.task(name="process_feedback_task")
def process_feedback_task(source: str, original_text: str, rating: float = None, author: str = None, app_version: str = None):
    """Async task to process NLP and save to DB."""
    db = SessionLocal()
    try:
        # 1. Analyze Sentiment
        sentiment_result = analyze_sentiment(original_text)
        
        # 2. Categorize
        category = "general"
        lower_text = original_text.lower()
        if "bug" in lower_text or "crash" in lower_text or "broken" in lower_text:
            category = "bug"
        elif "feature" in lower_text or "add" in lower_text or "please" in lower_text:
            category = "feature_request"

        # 3. Determine Urgency
        is_urgent = sentiment_result["label"] == "NEGATIVE" and category == "bug"

        # 4. Save
        db_feedback = Feedback(
            source=source,
            original_text=original_text,
            rating=rating,
            author=author,
            app_version=app_version,
            sentiment_score=sentiment_result["score"],
            sentiment_label=sentiment_result["label"],
            category=category,
            is_urgent=is_urgent,
            language=sentiment_result.get("language", "en")
        )
        db.add(db_feedback)
        
        # 5. Generate Alert if Urgent
        if is_urgent:
            alert = Alert(
                message=f"Urgent Issue Detected from {source}: {original_text[:100]}...",
                severity="HIGH"
            )
            db.add(alert)
            
        db.commit()
        return db_feedback.id
    except Exception as e:
        logger.error(f"Error in process_feedback_task: {e}")
        db.rollback()
    finally:
        db.close()

@celery_app.task(name="ingest_playstore_task")
def ingest_playstore_task(app_id: str, count: int):
    """Async task to scrape play store and spawn processing tasks."""
    raw_feedbacks = fetch_google_play_reviews(app_id, count)
    for fb in raw_feedbacks:
        process_feedback_task.delay(
            source=fb["source"],
            original_text=fb["original_text"],
            rating=fb["rating"],
            author=fb["author"],
            app_version=fb["app_version"]
        )
    return f"Triggered processing for {len(raw_feedbacks)} Play Store reviews."

@celery_app.task(name="ingest_appstore_task")
def ingest_appstore_task(app_name: str, app_id: int, count: int):
    """Async task to scrape App Store and spawn processing tasks."""
    raw_feedbacks = fetch_app_store_reviews(app_name, app_id, count)
    for fb in raw_feedbacks:
        process_feedback_task.delay(
            source=fb["source"],
            original_text=fb["original_text"],
            rating=fb["rating"],
            author=fb["author"],
            app_version=fb["app_version"]
        )
    return f"Triggered processing for {len(raw_feedbacks)} App Store reviews."
