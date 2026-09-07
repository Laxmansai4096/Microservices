# Complete Code & Infrastructure Implementation Guide for Azure Function App Features

This guide provides exact **Python v2 code implementations**, **Azure CLI configuration commands**, and **architectural setup** for every core Azure Function App feature.

---

## 1. HTTP Trigger & Ingress Routing Implementation

### Python Code (`function_app.py`)
```python
import azure.functions as func
import json
import logging

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="analyze-text", methods=["POST", "GET"])
def analyze_text(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Processing HTTP request for text analysis.")
    
    text = req.params.get('text')
    if not text:
        try:
            req_body = req.get_json()
            if isinstance(req_body, dict):
                text = req_body.get('text')
        except ValueError:
            pass

    if not text:
        return func.HttpResponse(
            json.dumps({"error": "Missing 'text' parameter in request."}),
            status_code=400,
            mimetype="application/json"
        )

    return func.HttpResponse(
        json.dumps({
            "status": "success",
            "received_text": text,
            "word_count": len(text.split())
        }),
        status_code=200,
        mimetype="application/json"
    )
```

### Azure Deployment Command
```powershell
az functionapp create `
  --resource-group rg-explore-ai `
  --consumption-plan-location eastus `
  --runtime python `
  --runtime-version 3.10 `
  --functions-version 4 `
  --name func-ai-microservice-65064 `
  --storage-account stexploreai65064 `
  --os-type Linux
```

---

## 2. Dynamic Scale-to-Zero ($0 Idle Cost) Implementation

### How It Works in Code & Configuration
Scale-to-Zero is enabled natively by deploying to the **Consumption (Dynamic) Plan**. No custom code is required; the Azure Scale Controller handles worker termination automatically after ~5 minutes of idle time.

### Verification CLI Commands
```powershell
# Check current plan SKU (Dynamic / Consumption)
az functionapp show `
  --name func-ai-microservice-65064 `
  --resource-group rg-explore-ai `
  --query "{Name:name, Plan:appServicePlanId, State:state}" `
  --output table
```

---

## 3. Warm Provisioned Instances ("Always On") Implementation

### Azure CLI Configuration Command
To eliminate cold starts for latency-critical production APIs, enable `alwaysOn` on Dedicated/App Service plans or set pre-warmed instances on Flex/Premium plans.

```powershell
# Enable Always On via CLI
az functionapp config set `
  --name func-ai-microservice-65064 `
  --resource-group rg-explore-ai `
  --always-on true
```

---

## 4. Rich Event-Driven Triggers (Blob Storage & Service Bus Queue)

### A. Blob Trigger (Document Ingestion / RAG Pipeline)
Executes automatically whenever a PDF or document is uploaded to Azure Blob Storage container `ai-documents`.

```python
@app.blob_trigger(
    arg_name="myblob",
    path="ai-documents/{name}",
    connection="AzureWebJobsStorage"
)
def process_document_blob(myblob: func.InputStream):
    logging.info(f"Blob Trigger fired for file: {myblob.name}, Size: {myblob.length} bytes")
    
    # Read document content
    content = myblob.read()
    
    # Example: Perform Document Intelligence OCR or chunking here
    logging.info(f"Successfully processed document {myblob.name} for AI embedding pipeline.")
```

### B. Service Bus Queue Trigger (Asynchronous AI Worker)
Executes worker tasks off a queue to handle high-volume AI tasks without hitting API rate limits.

```python
@app.servicebus_queue_trigger(
    arg_name="msg",
    queue_name="ai-task-queue",
    connection="ServiceBusConnectionString"
)
def process_queued_ai_task(msg: func.ServiceBusMessage):
    logging.info(f"Received Service Bus message: {msg.get_body().decode('utf-8')}")
    # Run long-running AI embedding or DB indexing task here
```

---

## 5. Application Settings & Environment Variable Implementation

### Accessing Settings in Python
```python
import os

# Retrieve App Settings injected into OS environment
OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_KEY")
MODEL_NAME = os.environ.get("AI_MODEL_VERSION", "gpt-4o-mini")
SYSTEM_PROMPT = os.environ.get("SYSTEM_PROMPT", "Default assistant prompt")
```

### Azure CLI Configuration Command
```powershell
az functionapp config appsettings set `
  --name func-ai-microservice-65064 `
  --resource-group rg-explore-ai `
  --settings `
    AZURE_OPENAI_KEY="sk-azure-123456789" `
    AI_MODEL_VERSION="gpt-4o-v2" `
    SYSTEM_PROMPT="You are a helpful customer support AI."
```

---

## 6. Real-Time Log Streaming Implementation

### Python Code Logging Pattern
```python
import logging

@app.route(route="log-demo", methods=["GET"])
def log_demo(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("ℹ️ Information: Function call initiated.")
    logging.warning("⚠️ Warning: Request payload missing optional parameter.")
    logging.error("❌ Error: Failed to reach external vector store.")
    return func.HttpResponse("Logged successfully.")
```

### CLI Command to View Live Output
```powershell
az functionapp log tail --name func-ai-microservice-65064 --resource-group rg-explore-ai
```

---

## 7. Deployment Slots (Staging Environment) Implementation

### Azure CLI Commands for Zero-Downtime Deployments
```powershell
# 1. Create a Staging Deployment Slot
az functionapp deployment slot create `
  --name func-ai-microservice-65064 `
  --resource-group rg-explore-ai `
  --slot staging

# 2. Deploy updated code to Staging Slot
# (Publish command targets the staging slot)

# 3. Swap Staging to Production (Zero Downtime)
az functionapp deployment slot swap `
  --name func-ai-microservice-65064 `
  --resource-group rg-explore-ai `
  --slot staging `
  --target-slot production
```

---

## 8. Passwordless Managed Identity Authentication Implementation

### Python Code (`azure-identity` integration)
No hardcoded passwords or API keys needed. Uses Azure Entra ID token authentication.

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import os

# Initialize passwordless credential from Managed Identity environment
credential = DefaultAzureCredential()

# Access Key Vault securely
vault_url = os.environ.get("KEY_VAULT_URL")
secret_client = SecretClient(vault_url=vault_url, credential=credential)

# Fetch secret without hardcoded keys
secret_val = secret_client.get_secret("MyAiSecretKey").value
```

### Azure CLI Identity Assignment Command
```powershell
# Assign System Identity
az functionapp identity assign `
  --name func-ai-microservice-65064 `
  --resource-group rg-explore-ai
```

---

## 9. Application Insights Telemetry Implementation

### Configuration in `host.json`
```json
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "maxTelemetryItemsPerSecond": 20
      }
    }
  },
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[4.*, 5.0.0)"
  }
}
```

### Linking Connection String via CLI
```powershell
$AI_CONN_STRING = az monitor app-insights component show --app ai-insights-explore --resource-group rg-explore-ai --query connectionString -o tsv

az functionapp config appsettings set `
  --name func-ai-microservice-65064 `
  --resource-group rg-explore-ai `
  --settings APPLICATIONINSIGHTS_CONNECTION_STRING=$AI_CONN_STRING
```
