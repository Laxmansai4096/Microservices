import azure.functions as func
import logging
import json
import re

# Initialize Azure Function App with Anonymous Auth level for HTTP routes
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="analyze-text", methods=["POST", "GET"])
def analyze_text(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing text analysis request via Azure Functions Microservice.')

    # 1. Retrieve text from query string parameter or JSON request body
    text = req.params.get('text')
    if not text:
        try:
            req_body = req.get_json()
        except Exception:
            req_body = None
        if req_body and isinstance(req_body, dict):
            text = req_body.get('text')

    # 2. Return 400 Bad Request if no text provided
    if not text:
        return func.HttpResponse(
            json.dumps({
                "status": "error",
                "message": "Please supply a 'text' parameter in query string or JSON payload body.",
                "usage_example": {
                    "GET": "/api/analyze-text?text=Azure+Functions+are+awesome",
                    "POST": {"text": "Azure Functions are awesome and fast!"}
                }
            }, indent=2),
            status_code=400,
            mimetype="application/json"
        )

    # 3. Perform Microservice logic (Tokenization, Metrics, Sentiment Classification)
    words = re.findall(r'\w+', text)
    word_count = len(words)
    char_count = len(text)

    positive_words = {"great", "good", "awesome", "excellent", "fast", "love", "amazing", "happy", "success", "clean", "easy", "powerful"}
    negative_words = {"bad", "slow", "error", "fail", "terrible", "poor", "hate", "issue", "bug", "crash", "hard", "expensive"}

    lowered_words = [w.lower() for w in words]
    pos_score = sum(1 for w in lowered_words if w in positive_words)
    neg_score = sum(1 for w in lowered_words if w in negative_words)

    if pos_score > neg_score:
        sentiment = "Positive 😁"
    elif neg_score > pos_score:
        sentiment = "Negative 😞"
    else:
        sentiment = "Neutral 😐"

    response_payload = {
        "service": "Azure Functions Text Processor",
        "microservice_type": "Serverless FaaS",
        "status": "success",
        "analysis": {
            "input_text": text,
            "word_count": word_count,
            "character_count": char_count,
            "sentiment": sentiment,
            "positive_score": pos_score,
            "negative_score": neg_score
        },
        "system_info": {
            "cloud_provider": "Microsoft Azure",
            "trigger_type": "HTTP Event Trigger",
            "scaling_model": "Dynamic Consumption (Auto scale to 0)"
        }
    }

    return func.HttpResponse(
        json.dumps(response_payload, indent=2),
        status_code=200,
        mimetype="application/json"
    )

@app.route(route="health", methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Health check ping received.')
    return func.HttpResponse(
        json.dumps({
            "status": "healthy",
            "service": "azure-functions-text-analyzer",
            "message": "Azure Functions Microservice is online and responding."
        }, indent=2),
        status_code=200,
        mimetype="application/json"
    )
