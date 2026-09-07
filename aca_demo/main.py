from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import socket
import datetime

app = FastAPI(
    title="Azure Container Apps AI Microservice",
    description="Live AI Agent Microservice running on ACA Environment cae-explore-ai",
    version="1.0.0"
)

class SentimentRequest(BaseModel):
    text: str

class SentimentResponse(BaseModel):
    text: str
    sentiment: str
    confidence: float
    processed_by: str
    timestamp: str

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "ACA AI Microservice Demo",
        "hostname": socket.gethostname(),
        "environment": os.getenv("CONTAINER_APP_ENV", "cae-explore-ai"),
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "uptime": "ok"}

@app.post("/ai/analyze", response_model=SentimentResponse)
def analyze_sentiment(request: SentimentRequest):
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    text_lower = request.text.lower()
    if any(word in text_lower for word in ["great", "excellent", "awesome", "good", "love", "fantastic", "amazing"]):
        sentiment = "Positive"
        confidence = 0.95
    elif any(word in text_lower for word in ["bad", "poor", "terrible", "slow", "error", "horrible", "fail"]):
        sentiment = "Negative"
        confidence = 0.91
    else:
        sentiment = "Neutral"
        confidence = 0.78

    return SentimentResponse(
        text=request.text,
        sentiment=sentiment,
        confidence=confidence,
        processed_by=f"ACA Replica ({socket.gethostname()})",
        timestamp=datetime.datetime.utcnow().isoformat()
    )
