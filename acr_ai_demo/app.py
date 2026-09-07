import time
from fastapi import FastAPI

app = FastAPI(title="ACR AI Model Microservice", version="1.0")

@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "service": "ACR AI Microservice Demo",
        "container_registry": "acrexploreai65064.azurecr.io"
    }

@app.post("/predict")
def predict_ai(prompt: str):
    return {
        "prompt": prompt,
        "response": f"AI Insight: Processed prompt '{prompt}' inside container from ACR!",
        "timestamp": time.time()
    }
