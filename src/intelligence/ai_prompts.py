def generate_insight_summary(stats: dict, top_issues: list) -> str:
    """
    Simulates an AI generating a text summary based on data.
    In a true production environment, this could hook into a local LLM via Ollama
    or HuggingFace transformers (e.g., LLaMA 3 8B or Flan-T5) to generate text.
    """
    total = stats.get("total_feedback", 0)
    pos = stats.get("sentiment_distribution", {}).get("positive", 0)
    bugs = stats.get("total_bugs", 0)
    
    if total == 0:
        return "Not enough data collected this week to generate AI insights."
    
    pos_ratio = pos / total if total > 0 else 0
    sentiment_trend = "positive" if pos_ratio >= 0.5 else "concerningly negative"
    
    insight = (
        f"AI Executive Summary: This week, the overall user sentiment trend was {sentiment_trend}. "
        f"We processed {total} total pieces of feedback across all channels. "
    )
    
    if bugs > 0:
        insight += f"There were {bugs} critical bugs identified by the NLP engine. "
        if top_issues:
            # Extract a snippet from the top issue
            top_issue_text = top_issues[0].get('original_text', '')[:60].replace('\n', ' ')
            insight += f"The most recurring theme among negative feedback was related to: '{top_issue_text}...' "
            
    insight += "Recommendation: Prioritize resolving the top flagged issues in the next sprint to improve CSAT metrics."
    
    return insight

def generate_suggested_response(feedback_text: str, sentiment: str, category: str, language: str = "en") -> str:
    """
    Simulates an AI generating a contextual reply to a customer review.
    """
    if language != "en":
        return "Thank you for your feedback! (Auto-reply in English. Full multilingual generation coming soon.)"
        
    if sentiment == "POSITIVE":
        if category == "feature_request":
            return "Thank you so much for the 5-star review! We love your feature idea and have passed it to our product team."
        return "Thank you for the wonderful review! We're thrilled you're enjoying the app."
        
    elif sentiment == "NEGATIVE":
        if category == "bug":
            return "We sincerely apologize for the crashes you're experiencing. Our engineering team has been alerted and we are working on a fix ASAP. Please reach out to support@feedbackiq.com if you need immediate assistance."
        return "We're sorry to hear you had a frustrating experience. We are constantly working to improve and value your feedback."
        
    # NEUTRAL
    return "Thank you for your feedback. We appreciate you taking the time to share your thoughts with us."
