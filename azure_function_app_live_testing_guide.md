# Hands-On Azure Function App Feature Testing & Learning Guide

This document provides an interactive, feature-by-feature testing laboratory for **Azure Function Apps** deployed live in your Azure Cloud environment (`rg-explore-ai` / `func-ai-microservice-65064`). Each section breaks down:
1. **What the feature is and how it works**
2. **Why it is useful for real-world AI microservices**
3. **Pros and Cons of the feature**
4. **Step-by-step terminal commands to test and observe the feature live in your Azure environment** using Azure CLI (`az login`), PowerShell (`Invoke-RestMethod`), and `curl`.

---

## Interactive Feature Index
- [Feature 1: HTTP Event Trigger & Ingress Routing](#feature-1-http-event-trigger--ingress-routing)
- [Feature 2: Dynamic Consumption Scale-to-Zero ($0 Idle Cost) & Cold Start](#feature-2-dynamic-consumption-scale-to-zero-0-idle-cost--cold-start)
- [Feature 3: Warm Provisioned Instances ("Always On" / Premium Tier)](#feature-3-warm-provisioned-instances-always-on--premium-tier)
- [Feature 4: Automatic Event-Driven Autoscaling (Azure Scale Controller)](#feature-4-automatic-event-driven-autoscaling-azure-scale-controller)
- [Feature 5: Application Settings & Environment Variable Management](#feature-5-application-settings--environment-variable-management)
- [Feature 6: Real-Time Live Log Streaming (`log tail`)](#feature-6-real-time-live-log-streaming-log-tail)
- [Feature 7: Deployment Slots & Staging Environments](#feature-7-deployment-slots--staging-environments)
- [Feature 8: Managed Identity & Passwordless Entra ID Authentication](#feature-8-managed-identity--passwordless-entra-id-authentication)
- [Feature 9: Application Insights & Distributed Telemetry Tracing](#feature-9-application-insights--distributed-telemetry-tracing)

---

## Feature 1: HTTP Event Trigger & Ingress Routing

### What It Does
Azure Function Apps use decorator-based HTTP triggers (`@app.route()`) in the Python v2 programming model. Azure automatically provisions an HTTPS endpoint with managed TLS/SSL certificates (`https://<app-name>.azurewebsites.net/api/<route>`) and routes incoming HTTP GET/POST requests directly to the serverless function execution handler.

### Why It Is Useful
- Provides lightweight, high-performance REST APIs for text processing, embedding calculations, and AI agent tool/plugin callbacks.
- Out-of-the-box secure HTTPS domain with zero manual web server or ingress setup.

### Pros & Cons
- **Pros**: Automatic HTTPS configuration, zero reverse-proxy maintenance, support for JSON payloads, parameters, and custom headers.
- **Cons**: Subject to HTTP request timeout limits (5 minutes by default on Consumption Plan).

### Step-by-Step Live Test

#### Step 1: Login to Azure CLI & Verify Deployment
```powershell
az login
az functionapp show `
  --name func-ai-microservice-65064 `
  --resource-group rg-explore-ai `
  --query "{Name:name, State:state, Host:defaultHostName, Location:location}" `
  --output table
```

#### Step 2: Test Live Health Endpoint
```powershell
Invoke-RestMethod -Uri "https://func-ai-microservice-65064.azurewebsites.net/api/health" -Method Get | ConvertTo-Json
```

#### Step 3: Test AI Text Processing Endpoint (GET Request)
```powershell
Invoke-RestMethod -Uri "https://func-ai-microservice-65064.azurewebsites.net/api/analyze-text?text=Azure+Functions+are+fast+and+awesome" -Method Get | ConvertTo-Json
```

#### Expected Result
Returns HTTP 200 with structured JSON sentiment analysis, word count, character count, and system metadata from the live cloud worker.

---

## Feature 2: Dynamic Consumption Scale-to-Zero ($0 Idle Cost) & Cold Start

### What It Does
In the **Consumption Plan**, when no HTTP requests arrive for a period of time, Azure Function App scales active compute workers down to **0**. When a new event arrives, the Azure Scale Controller spins up a Python worker process on demand to handle the request.

### Why It Is Useful
- **100% Cost Optimization**: Pay strictly per execution millisecond. You pay **$0.00** when your application is idle.

### Pros & Cons
- **Pros**: Ideal for non-continuous workloads, background webhooks, and cost-sensitive dev/test environments. Includes 1 million free executions monthly.
- **Cons**: **Cold Start Latency** — The initial request after an idle period may take 2 to 6 seconds while Python loads dependencies and initializes runtime.

### Step-by-Step Live Test

#### Step 1: Measure Response Time After Idle (Cold Start vs Warm Start)
Run a timed request using PowerShell:
```powershell
Measure-Command { 
  Invoke-RestMethod -Uri "https://func-ai-microservice-65064.azurewebsites.net/api/health" 
} | Select-Object TotalMilliseconds, TotalSeconds
```

#### Step 2: Immediate Follow-up Test (Warm Instance)
Run the exact same command immediately again:
```powershell
Measure-Command { 
  Invoke-RestMethod -Uri "https://func-ai-microservice-65064.azurewebsites.net/api/health" 
} | Select-Object TotalMilliseconds, TotalSeconds
```

#### Expected Result
- **First request (Cold Start)**: Takes ~1,500 – 4,000 ms.
- **Second request (Warm Start)**: Takes **< 150 ms** because the Python runtime is already warmed up in memory.

---

## Feature 3: Warm Provisioned Instances ("Always On" / Premium Tier)

### What It Does
For applications that cannot tolerate cold start delays, Azure offers **Always On** (Dedicated/App Service Plan) or **Pre-warmed Instances** (Premium / Flex Consumption Plan) to keep at least one instance pre-allocated and ready 24/7.

### Why It Is Useful
- Eliminates cold starts completely for critical user-facing AI endpoints, real-time chat UIs, and latency-sensitive SLAs.

### Pros & Cons
- **Pros**: Predictable, sub-second latency for 100% of user requests.
- **Cons**: Incurs continuous baseline compute billing regardless of traffic volume.

### Step-by-Step Live Test

#### Step 1: Check Current Always-On Configuration
```powershell
az functionapp config show `
  --name func-ai-microservice-65064 `
  --resource-group rg-explore-ai `
  --query "alwaysOn" `
  --output json
```

#### Step 2: Toggle Always-On Setting (Applicable for B1/S1/P1 Tier Plans)
```powershell
az functionapp config set `
  --name func-ai-microservice-65064 `
  --resource-group rg-explore-ai `
  --always-on true
```

#### Expected Result
Always-On status updates to `true`, instructing Azure to keep worker hosts in memory continuously.

---

## Feature 4: Automatic Event-Driven Autoscaling (Azure Scale Controller)

### What It Does
Azure Function Apps rely on an independent component called the **Azure Scale Controller**. It continuously monitors request metrics, queue lengths, and event rates. When incoming request traffic increases, the Scale Controller automatically provisions additional worker instances (scaling up to 200 instances on Consumption Plan).

### Why It Is Useful
- Seamlessly absorbs sudden traffic spikes (e.g. hundreds of concurrent users sending text for sentiment analysis or LLM processing) without manual cluster tuning.

### Pros & Cons
- **Pros**: Zero cluster management, fully managed event-driven scaling up and down.
- **Cons**: Python global interpreter lock (GIL) limits concurrency per process; high volume requires scaling horizontal instances.

### Step-by-Step Live Test

#### Step 1: Query Plan and Max Scale Limit
```powershell
az functionapp show `
  --name func-ai-microservice-65064 `
  --resource-group rg-explore-ai `
  --query "{Plan:appServicePlanId, Kind:kind}" `
  --output json
```

#### Step 2: Simulate Concurrent Traffic Requests
Execute multiple parallel HTTP requests in PowerShell to trigger scaling:
```powershell
1..10 | ForEach-Object -Parallel {
  Invoke-RestMethod -Uri "https://func-ai-microservice-65064.azurewebsites.net/api/health"
}
```

#### Expected Result
All 10 parallel requests complete successfully in parallel with HTTP 200 OK.

---

## Feature 5: Application Settings & Environment Variable Management

### What It Does
Application Settings in Azure Function Apps are injected into the Python runtime as standard OS environment variables (`os.environ["SETTING_NAME"]`). They allow updating secrets, system prompts, API endpoints, or feature toggles without modifying or redeploying code.

### Why It Is Useful
- Dynamically tweak model names (e.g., switching from `gpt-4o-mini` to `gpt-4o`), model temperature, or API timeouts across environments instantly.

### Pros & Cons
- **Pros**: Decouples configuration from application code; encrypted at rest in Azure.
- **Cons**: Updating App Settings restarts the Function App host process (brief warm restart).

### Step-by-Step Live Test

#### Step 1: Add a New Application Setting
```powershell
az functionapp config appsettings set `
  --name func-ai-microservice-65064 `
  --resource-group rg-explore-ai `
  --settings AI_MODEL_VERSION="gpt-4o-v2" SYSTEM_PROMPT="You are an expert AI Assistant."
```

#### Step 2: Verify Key Value Pair in Azure Cloud
```powershell
az functionapp config appsettings list `
  --name func-ai-microservice-65064 `
  --resource-group rg-explore-ai `
  --query "[?name=='AI_MODEL_VERSION' || name=='SYSTEM_PROMPT'].{Name:name, Value:value}" `
  --output table
```

#### Expected Result
Output confirms `AI_MODEL_VERSION` is set to `gpt-4o-v2` and `SYSTEM_PROMPT` is configured live in Azure.

---

## Feature 6: Real-Time Live Log Streaming (`log tail`)

### What It Does
Azure CLI streams `stdout`, `stderr`, and Python `logging.info()` outputs directly from the running cloud function instance to your local terminal in real time.

### Why It Is Useful
- Indispensable for live debugging, inspecting input payloads, timing LLM calls, and diagnosing runtime exceptions as users interact with your cloud API.

### Pros & Cons
- **Pros**: Instant visibility into live execution without navigating portal UI or waiting for Log Analytics ingestion delay.
- **Cons**: Requires active CLI session connection.

### Step-by-Step Live Test

#### Step 1: Open Terminal and Start Streaming Logs
```powershell
az functionapp log tail `
  --name func-ai-microservice-65064 `
  --resource-group rg-explore-ai
```

#### Step 2: Trigger an HTTP Request in Another Terminal Window
```powershell
Invoke-RestMethod -Uri "https://func-ai-microservice-65064.azurewebsites.net/api/analyze-text?text=Testing+live+log+tailing"
```

#### Expected Result
The `log tail` window displays live logs:
`Processing text analysis request via Azure Functions Microservice.`
`Executed 'Functions.analyze_text' (Succeeded, Id=..., Duration=...ms)`

---

## Feature 7: Deployment Slots & Staging Environments

### What It Does
Deployment Slots are live apps with their own hostnames. You can deploy updated code to a `staging` slot, verify functionality in production cloud environment, and then perform a **zero-downtime swap** with the `production` slot.

### Why It Is Useful
- Test major AI prompt changes, python library updates, or framework upgrades safely without impacting live production users.

### Pros & Cons
- **Pros**: Zero-downtime deployments, immediate rollback capability by swapping back.
- **Cons**: Slots share underlying plan resources on dedicated tiers.

### Step-by-Step Live Test

#### Step 1: List Existing Slots for the Function App
```powershell
az functionapp deployment slot list `
  --name func-ai-microservice-65064 `
  --resource-group rg-explore-ai `
  --output table
```

#### Step 2: Create a Staging Deployment Slot
```powershell
az functionapp deployment slot create `
  --name func-ai-microservice-65064 `
  --resource-group rg-explore-ai `
  --slot staging
```

#### Expected Result
Creates a staging slot with endpoint `https://func-ai-microservice-65064-staging.azurewebsites.net`.

---

## Feature 8: Managed Identity & Passwordless Entra ID Authentication

### What It Does
Assigns an **Azure Entra ID (Azure AD) Managed Identity** to the Function App. Azure handles credential management and token rotation automatically, allowing your Python code to authenticate with Azure AI Search, Azure OpenAI, Key Vault, and Blob Storage without embedding keys or passwords.

### Why It Is Useful
- Eliminates hardcoded API keys in code or configuration files, satisfying enterprise zero-trust security standards.

### Pros & Cons
- **Pros**: Passwordless security, zero key rotation overhead, fine-grained RBAC permission control.
- **Cons**: Target Azure resources must support Entra ID authentication and have RBAC roles assigned.

### Step-by-Step Live Test

#### Step 1: Enable System-Assigned Managed Identity
```powershell
az functionapp identity assign `
  --name func-ai-microservice-65064 `
  --resource-group rg-explore-ai
```

#### Step 2: Verify Principal ID
```powershell
az functionapp identity show `
  --name func-ai-microservice-65064 `
  --resource-group rg-explore-ai `
  --query "{PrincipalId:principalId, TenantId:tenantId, Type:type}" `
  --output json
```

#### Expected Result
Returns `principalId` GUID representing your Function App's unique service identity in Azure Entra ID.

---

## Feature 9: Application Insights & Distributed Telemetry Tracing

### What It Does
Application Insights automatically collects performance telemetry, request durations, failure counts, exception stack traces, and external dependency calls made by your Azure Function App.

### Why It Is Useful
- Essential for monitoring end-to-end latency in complex AI microservices (e.g. measuring how long document OCR took vs LLM inference vs vector DB indexing).

### Pros & Cons
- **Pros**: Automatic telemetry collection, queryable using Kusto Query Language (KQL), visual application map.
- **Cons**: Minor logging ingestion cost for high-volume logs (can be controlled via sampling).

### Step-by-Step Live Test

#### Step 1: Verify Application Insights Connection String
```powershell
az functionapp config appsettings list `
  --name func-ai-microservice-65064 `
  --resource-group rg-explore-ai `
  --query "[?name=='APPLICATIONINSIGHTS_CONNECTION_STRING'].{Name:name, Value:value}" `
  --output table
```

#### Step 2: View App Insights Resources in Resource Group
```powershell
az monitor app-insights component show `
  --resource-group rg-explore-ai `
  --query "[].{Name:name, Location:location, AppId:appId}" `
  --output table
```

#### Expected Result
Confirms Application Insights telemetry integration is active and linked to `func-ai-microservice-65064`.

---

## Feature Summary Reference Matrix

| Feature | Primary Purpose | Best AI / Microservice Use Case | Cost Impact |
| :--- | :--- | :--- | :--- |
| **HTTP Trigger** | REST API Ingress & HTTPS routing | Text processing, Agent tool plugins, Webhooks | Free built-in feature |
| **Scale to Zero** | Shutdown compute when idle | Dev/test, low-frequency event processing | **$0 when idle** |
| **Always On / Warm** | Eliminate cold starts 24/7 | Production latency-sensitive APIs | Continuous plan baseline |
| **Scale Controller** | Dynamic event-driven scaling | High-concurrency traffic bursts | Scales per execution millisecond |
| **App Settings** | Managed environment variables | Dynamic AI prompt & model version tweaks | Included |
| **Log Tail (`az`)** | Real-time CLI stdout streaming | Live prompt execution debugging | Free CLI tool |
| **Deployment Slots** | Staging slots & zero-downtime swap | Prompt engineering & model A/B testing | Free on standard/dedicated plans |
| **Managed Identity** | Passwordless Entra ID authentication | Secure access to Key Vault & AI Search | Free built-in feature |
| **App Insights** | End-to-end distributed tracing | AI pipeline bottleneck & latency profiling | Minimal telemetry ingestion |
