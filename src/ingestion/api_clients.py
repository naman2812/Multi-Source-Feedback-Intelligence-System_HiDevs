from google_play_scraper import reviews, Sort
from app_store_scraper import AppStore
import pandas as pd
import logging
import datetime

logger = logging.getLogger(__name__)

def fetch_google_play_reviews(app_id: str = "com.spotify.music", count: int = 50):
    """Fetch recent reviews from Google Play Store."""
    try:
        result, _ = reviews(
            app_id,
            lang='en',
            country='us',
            sort=Sort.NEWEST,
            count=count
        )
        
        feedbacks = []
        for r in result:
            feedbacks.append({
                "source": "google_play",
                "author": r.get("userName"),
                "original_text": r.get("content"),
                "rating": float(r.get("score")) if r.get("score") else None,
                "app_version": r.get("reviewCreatedVersion")
            })
        return feedbacks
    except Exception as e:
        logger.error(f"Error fetching Play Store reviews: {e}")
        return []

def fetch_app_store_reviews(app_name: str = "spotify-music-and-podcasts", app_id: int = 324684580, count: int = 20):
    """Fetch recent reviews from the Apple App Store."""
    try:
        app = AppStore(country='us', app_name=app_name, app_id=app_id)
        # Note: app_store_scraper is synchronous and can block, which is why it runs in Celery
        app.review(how_many=count)
        
        feedbacks = []
        for r in app.reviews:
            feedbacks.append({
                "source": "app_store",
                "author": r.get("userName"),
                "original_text": r.get("review"),
                "rating": float(r.get("rating")) if r.get("rating") else None,
                "app_version": None # app-store-scraper doesn't always provide version reliably
            })
        return feedbacks
    except Exception as e:
        logger.error(f"Error fetching App Store reviews: {e}")
        return []

def fetch_csv_reviews(filepath: str):
    """Ingest reviews from a CSV file."""
    try:
        df = pd.read_csv(filepath)
        # Expected columns: text, rating, author
        feedbacks = []
        for _, row in df.iterrows():
            # Skip empty text
            text = str(row.get("text", ""))
            if not text or text == "nan":
                continue
                
            feedbacks.append({
                "source": "csv",
                "original_text": text,
                "rating": float(row.get("rating", 0.0)) if pd.notna(row.get("rating")) else None,
                "author": str(row.get("author", "Unknown"))
            })
        return feedbacks
    except Exception as e:
        logger.error(f"Error reading CSV: {e}")
        return []
