import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Feedback Intelligence API is running"}

def test_get_stats():
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_feedback" in data
    assert "sentiment_distribution" in data

def test_get_feedback():
    response = client.get("/api/feedback")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_ingest_playstore():
    # Test triggering the async task
    response = client.post("/api/ingest/playstore?app_id=com.spotify.music&count=1")
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"

def test_ingest_appstore():
    response = client.post("/api/ingest/appstore?app_name=spotify&app_id=324684580&count=1")
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"
