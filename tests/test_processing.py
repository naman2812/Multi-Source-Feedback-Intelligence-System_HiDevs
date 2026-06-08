import pytest
from src.processing.analyzer import analyze_sentiment
from src.intelligence.ai_prompts import generate_insight_summary

def test_analyze_sentiment_positive():
    result = analyze_sentiment("I absolutely love this app, it is the best!")
    assert result["label"] == "POSITIVE"
    assert result["score"] > 0.0

def test_analyze_sentiment_negative():
    result = analyze_sentiment("This is terrible, it crashes every time I open it. Bug!")
    assert result["label"] == "NEGATIVE"
    assert result["score"] < 0.0

def test_analyze_sentiment_empty():
    result = analyze_sentiment("")
    assert result["label"] == "NEUTRAL"
    assert result["score"] == 0.0

def test_generate_insight_summary():
    stats = {
        "total_feedback": 100,
        "sentiment_distribution": {"positive": 80, "negative": 10, "neutral": 10},
        "total_bugs": 5
    }
    top_issues = [{"original_text": "Login page crash"}]
    
    summary = generate_insight_summary(stats, top_issues)
    assert "positive" in summary.lower()
    assert "100" in summary
    assert "5" in summary
    assert "Login page crash" in summary

def test_generate_insight_summary_empty():
    summary = generate_insight_summary({}, [])
    assert "Not enough data" in summary
