# Azure Service Bus: Feature-by-Feature Tracing, Metrics & Hands-On Guide

---

## 🧭 Overview: How Azure Service Bus Stores Traces & Metrics

Azure Service Bus provides 3 levels of visibility into your past and current messaging operations:

1. **Service Bus Explorer (State Inspection)**: Live inspection of active messages, dead-letter messages, sequence numbers, system headers, and custom properties.
2. **Azure Monitor Metrics (Historical Charts & Progress)**: 1-minute to 30-day graphs showing incoming messages, outgoing messages, active message depth, and successful requests.
3. **Activity Logs & Diagnostic Settings (Audit Traces)**: Log of management actions (queue creation, policy updates, access key usage, connection attempts).

---

## 📑 Feature 1: Point-to-Point Message Queuing & Live Metrics

### What It Does:
Saves incoming messages in a First-In, First-Out (FIFO) queue (`ai-jobs-queue`). Decouples producers (web apps) from consumers (AI background workers).

### How to See Traces/Results of the Run I Executed:

#### 1. Via Azure Portal Metrics Graph:
- Go to [Azure Portal](https://portal.azure.com/) -> **Resource groups** -> **`rg-explore-ai`** -> **`sb-explore-ai`**.
- Click **Overview** in the left menu. Look at the **Metrics Charts**:
  - **Incoming Messages**: You will see spikes showing when our script sent 4 messages.
  - **Outgoing Messages**: You will see spikes showing when our consumer pulled and acknowledged the messages.
  - **Successful Requests**: Shows total successful AMQP/WebSocket calls.

#### 2. Via Azure CLI Command:
```bash
az servicebus queue show \
  --resource-group rg-explore-ai \
  --namespace-name sb-explore-ai \
  --name ai-jobs-queue \
  --query "countDetails" -o json
```
*Result of my run:* `activeMessageCount = 0`, `deadLetterMessageCount = 2`.

---

### Step-by-Step Instructions to Test Feature 1 Yourself:

1. Open PowerShell and navigate to `service_bus_demo`:
   ```bash
   cd c:\Users\2869026\Desktop\up\service_bus_demo
   ```
2. Run `producer.py` to send 3 new jobs:
   ```bash
   python producer.py
   ```
3. Immediately check the queue depth via CLI to see `activeMessageCount: 3`:
   ```bash
   az servicebus queue show --resource-group rg-explore-ai --namespace-name sb-explore-ai --name ai-jobs-queue --query "countDetails" -o json
   ```
4. Now run `consumer.py` to drain the queue back to 0:
   ```bash
   python consumer.py
   ```

---

## 💀 Feature 2: Dead-Letter Queue (DLQ) & Poison Message Inspection

### What It Does:
When a message fails processing repeatedly or contains corrupted data, Azure Service Bus moves it into a dedicated sub-queue called the **Dead-Letter Queue (DLQ)**. This prevents bad messages from blocking healthy traffic.

### How to See Traces/Results of the Run I Executed:

#### In Azure Portal (Exact UI Trace Path):
1. Go to **Azure Portal** -> **`rg-explore-ai`** -> **`sb-explore-ai`** -> **Queues** -> **`ai-jobs-queue`**.
2. Click **Service Bus Explorer** in the left menu.
3. At the top of the panel, click the **Queue type** dropdown and select **Dead-letter queue**.
4. Click **Peek from start** -> click on message `job-corrupt-a20ccc`.
5. Look at the **System Properties** box on the right:
   - **DeadLetterReason**: `UnreadableDocumentFormat`
   - **DeadLetterErrorDescription**: `File header corrupted or password protected.`
   - **DeliveryCount**: `2`
   - **EnqueuedTimeUtc**: Timestamp when it entered the DLQ.

---

### Step-by-Step Instructions to Test Feature 2 Yourself:

1. Send a corrupted message directly from Azure Portal:
   - Go to **`ai-jobs-queue`** -> **Service Bus Explorer** -> **Send messages**.
   - Body: `{"job_id": "test-poison-99", "corrupt": true}`.
   - Click **Send**.
2. Run the local consumer script:
   ```bash
   cd c:\Users\2869026\Desktop\up\service_bus_demo
   python consumer.py
   ```
3. Watch the terminal output: it will fail twice and log `[DLQ] Moving message 'test-poison-99' to Dead-Letter Queue...`.
4. Refresh the Azure Portal **Service Bus Explorer (Dead-letter queue)** tab to see your new dead-lettered message sitting in Azure!

---

## 🏷️ Feature 3: Application Properties & Custom Metadata Header Inspection

### What It Does:
Allows producers to attach key-value metadata to messages (e.g., `model = 'gpt-4o'`, `priority = 'HIGH'`). Consumers and Azure Functions can route messages based on headers without reading or parsing the message body.

### How to See Traces/Results of the Run I Executed:

In the terminal output of the run I executed:
```text
  [LOCK ACQUIRED] 'job-rag-9faa06'
     Payload: File='Annual_Financial_Report_2025.pdf'
     App Properties: {'model': 'text-embedding-3-small', 'priority': 'HIGH', 'task_type': 'rag_embeddings'}
```

---

### Step-by-Step Instructions to Test Feature 3 Yourself:

1. Send a message with custom headers from Azure Portal:
   - Go to **`ai-jobs-queue`** -> **Service Bus Explorer** -> **Send messages**.
   - Body: `{"text": "Hello AI World"}`
   - Under **Custom Properties**, click **Add Property**:
     - Key: `ai_model` | Value: `claude-3-5-sonnet`
     - Key: `priority` | Value: `VIP`
   - Click **Send**.
2. Click the **Peek** tab -> click **Peek from start**.
3. Select your message and click **Custom Properties** tab. You will see `ai_model: claude-3-5-sonnet` stored inside Azure metadata!

---

## 📡 Feature 4: Publish-Subscribe (Pub/Sub) Topics & Subscriptions

### What It Does:
Publishes an event to a **Topic** (`ai-events-topic`). Multiple **Subscriptions** (e.g., `analytics-sub`, `guardrails-sub`) independently receive copies of the event to process in parallel.

### How to See Traces/Results of the Run I Executed:

Query subscription metrics via CLI:
```bash
az servicebus topic subscription show \
  --resource-group rg-explore-ai \
  --namespace-name sb-explore-ai \
  --topic-name ai-events-topic \
  --name analytics-sub \
  --query "countDetails" -o json
```
*Result of my run:* `activeMessageCount = 1`.

---

### Step-by-Step Instructions to Test Feature 4 Yourself:

1. In PowerShell, publish an event to the topic:
   ```bash
   cd c:\Users\2869026\Desktop\up\service_bus_demo
   python topic_pubsub.py
   ```
2. Go to **Azure Portal** -> **`sb-explore-ai`** -> **Topics** -> **`ai-events-topic`** -> **Subscriptions** -> **`analytics-sub`**.
3. Click **Service Bus Explorer** -> **Peek from start**.
4. You will see the event `USER_PROMPT_SUBMITTED` sitting in the subscription waiting for an analytics agent!

---

## 📈 Feature 5: Azure Monitor Metrics & Activity Log Traces

### What It Does:
Tracks operational health, request rates, network traffic, authentication attempts, and errors over time.

### How to See Traces/Results in Azure Portal:

1. Go to **Azure Portal** -> **`sb-explore-ai`** (Service Bus Namespace).
2. Click **Activity log** in the left menu:
   - You will see historical audit events (e.g. `List Namespace Keys`, `Create Topic`, `Create Subscription`).
3. Click **Metrics** in the left menu (under Monitoring):
   - Metric: Select **Incoming Messages**.
   - Aggregation: Select **Sum**.
   - Change Time Range to **Last 1 hour**.
   - You will see a clear spike graph showing the exact minute we ran our tests!
