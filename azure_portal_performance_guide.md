# Step-by-Step Azure Portal GUI Guide: Exploring Function App Features & Performance

This guide walks you step-by-step through exploring, running, and analyzing performance for every Azure Function App feature visually inside your **Azure Portal Account** ([portal.azure.com](https://portal.azure.com)).

---

## Quick Navigation: Finding Your Function App in Azure Portal

1. Open your browser and log into [portal.azure.com](https://portal.azure.com).
2. In the top search bar, type **`func-ai-microservice-65064`** and click on your Function App.
3. Your Resource Group is **`rg-explore-ai`**.

---

## 1. Feature 1: HTTP Trigger & Ingress Execution

### How to Run & Test in Azure Portal:
1. In the left menu of **`func-ai-microservice-65064`**, click **Functions** (under *Functions* section).
2. Click on **`analyze-text`** function.
3. In the left sub-menu, click **Code + Test**.
4. Click the **Test/Run** button at the top bar.
5. In the right pane, select **HTTP Method: POST**.
6. Under **Body**, paste this JSON payload:
   ```json
   {
     "text": "Testing Azure Portal GUI execution for AI microservices!"
   }
   ```
7. Click **Run** button at the bottom.
8. View the **Output** tab to see HTTP 200 Response JSON.

> [!TIP]
> **CORS Resolution**: If Azure Portal displays a `Failed to fetch` error when running Code + Test, it means CORS (Cross-Origin Resource Sharing) needed `https://portal.azure.com` in its allowed origins. We have already updated this in your Azure Function App!

### How to See Performance in Azure Portal: 
1. Inside **`analyze-text`**, click **Overview** on the left sub-menu.
2. Observe 3 live graphs:
   - **Function Execution Count**: Total number of executions.
   - **Execution Units (MB-ms)**: Resource consumption used for billing.
   - **Error Count**: Failed executions (4xx / 5xx).

---

## 2. Feature 2: Dynamic Scale-to-Zero & Cold Start Performance

### How to See Cold Start vs Warm Performance in Azure Portal:
1. Navigate back to your main Function App **`func-ai-microservice-65064`**.
2. On the left sidebar menu, scroll to **Monitoring** and click **Metrics**.
3. Set the following options:
   - **Scope**: `func-ai-microservice-65064`
   - **Metric Namespace**: `Function App standard metrics`
   - **Metric**: **Function Execution Duration**
   - **Aggregation**: **Avg** / **Max**
4. Change the time range in top-right to **Last 30 minutes**.
5. **Observation**:
   - Notice spikes on the line chart (e.g. 1,500ms – 3,000ms) after periods of flat zero line — this visually shows **Cold Start** container initialization.
   - Subsequent rapid requests show flat low values (< 200ms) indicating **Warm Instance** execution.

---

## 3. Feature 3: Warm Provisioned Instances ("Always On")

### How to View & Configure in Azure Portal:
1. On the left menu under **Settings**, click **Environment variables** (or **Configuration**).
2. Click the **General settings** tab at the top.
3. Look for the **Always on** setting:
   - Toggle to **On** (keeps instances loaded 24/7).
   - Toggle to **Off** (enables scale-to-zero consumption).
4. Click **Save** at the bottom.

---

## 4. Feature 4: Real-Time Event-Driven Scaling (Live Metrics)

### How to View Live Server Scaling in Azure Portal:
1. On the left menu under **Monitoring**, click **Live Metrics** (or **Application Insights** ➔ **Live Metrics**).
2. A real-time dashboard opens showing:
   - **Live Servers / Replicas**: Shows active server host instances currently running.
   - **Incoming Request Rate**: Live graph of requests per second.
   - **Request Duration**: Live latency in milliseconds.
   - **Overall Health**: CPU & Memory usage across active server nodes.
3. Open a second browser tab and hit your API multiple times — watch the live graphs jump in real-time without refreshing the page!

---

## 5. Feature 5: Application Settings & Environment Variables

### How to View & Edit in Azure Portal:
1. On the left menu under **Settings**, click **Environment variables**.
2. Click the **App settings** tab.
3. You will see all key-value pairs stored in Azure Cloud:
   - `AI_MODEL_VERSION` = `gpt-4o-v2`
   - `SYSTEM_PROMPT` = `You are a helpful customer support AI`
4. Click on any variable to edit its value directly in the Portal GUI.
5. Click **Apply** ➔ Azure updates the setting and restarts the function host automatically.

---

## 6. Feature 6: Real-Time Log Streaming in Portal

### How to Watch Live Execution Logs in Azure Portal:
1. On the left menu under **Monitoring**, click **Log stream**.
2. Select **App Insights Logs** or **Filesystem Logs**.
3. Send a request to your API (`https://func-ai-microservice-65064.azurewebsites.net/api/health`).
4. Watch colored console logs (`[Information]`, `[Warning]`, `[Error]`) output line-by-line as requests hit Azure.

---

## 7. Feature 7: Deployment Slots (Staging vs Production)

### How to View & Swap Slots in Azure Portal:
1. On the left menu under **Deployment**, click **Deployment slots**.
2. See the list of slots (e.g. `production`, `staging`).
3. Click on **Swap** at the top action bar:
   - **Source**: `staging`
   - **Target**: `production`
4. View the side-by-side configuration diff preview.
5. Click **Swap** to perform a 1-click zero-downtime swap live in Azure.

---

## 8. Feature 8: Managed Identity & Passwordless Security

### How to View Managed Identity in Azure Portal:
1. On the left menu under **Settings**, click **Identity**.
2. Under **System assigned** tab:
   - **Status**: Enabled (`On`).
   - **Object (principal) ID**: Unique Azure Active Directory ID assigned to your app.
3. Click **Azure role assignments** button to see what Key Vaults, Databases, or Azure AI Search services this identity has permissions to access.

---

## 9. Feature 9: Application Insights End-to-End Tracing Performance

### How to View End-to-End Dependency & Latency Performance:
1. On the left menu under **Settings**, click **Application Insights**.
2. Click **View Application Insights data**.
3. On the Application Insights dashboard:
   - **Application Map**: Visual node map showing your Function App connected to databases, OpenAI APIs, and Blob Storage.
   - **Performance**: Breakdown of 50th, 95th, and 99th percentile response times.
   - **Failures**: Shows exact Python stack traces for any failed HTTP 500 requests.
