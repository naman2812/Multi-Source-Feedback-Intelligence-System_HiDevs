from langdetect import detect, DetectorFactory
import logging
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Ensure consistent language detection
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)

# Initialize lightweight lexicon analyzer
try:
    analyzer = SentimentIntensityAnalyzer()
except Exception as e:
    logger.error(f"Failed to initialize VaderSentiment: {e}")
    analyzer = None

def analyze_sentiment(text: str) -> dict:
    """
    Analyzes the sentiment of a given text using lightweight heuristics.
    Returns a dict with 'label' (POSITIVE/NEGATIVE/NEUTRAL) and 'score' (-1.0 to 1.0).
    """
    if not text or not text.strip():
        return {"label": "NEUTRAL", "score": 0.0}
    
    # Truncate text to 512 chars for safety
    truncated_text = text[:512]
    
    # Determine language
    try:
        language = detect(truncated_text)
    except:
        language = "unknown"
        
    if analyzer:
        try:
            # Get compound score from -1.0 to +1.0
            scores = analyzer.polarity_scores(truncated_text)
            compound = scores['compound']
            # Context-aware override for subtle complaints that Vader misses
            lower_text = truncated_text.lower()
            negative_keywords = ['deducted', 'charged', 'refund', 'scam', 'crash', 'stuck', 'not working', 'broken', 'free plan', 'issue', 'bug', 'fail']
            
            if any(word in lower_text for word in negative_keywords):
                label = "NEGATIVE"
                compound = -0.5 # override score
            elif compound >= 0.05:
                label = "POSITIVE"
            elif compound <= -0.05:
                label = "NEGATIVE"
            else:
                label = "NEUTRAL"    
            return {"label": label, "score": compound, "language": language}
        except Exception as e:
            logger.error(f"Error during sentiment analysis: {e}")
            
    # Simple fallback heuristic if Vader fails
    lower_text = truncated_text.lower()
    if any(word in lower_text for word in ['great', 'awesome', 'good', 'love', 'best', 'excellent']):
        return {"label": "POSITIVE", "score": 0.8, "language": language}
    elif any(word in lower_text for word in ['bad', 'terrible', 'worst', 'hate', 'bug', 'crash', 'fail']):
        return {"label": "NEGATIVE", "score": -0.8, "language": language}
        
    return {"label": "NEUTRAL", "score": 0.0, "language": language}
