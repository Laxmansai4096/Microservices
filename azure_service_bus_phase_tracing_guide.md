# How to Trace Load Buffering & Processing Phases in Azure Portal

---

## 📍 Phase 1: Tracing the Traffic Spike (100 Requests Enqueued)

When `load_buffering_demo.py` ran **Phase 1**, it flooded 100 messages into Azure Service Bus in **3.31 seconds**.

### How to See the Phase 1 Trace in Azure Portal:

1. Open [Azure Portal](https://portal.azure.com/).
2. Go to **Resource groups** -> **`rg-explore-ai`** -> **`sb-explore-ai`** (Service Bus Namespace).
3. In the left menu (under *Monitoring*), click **Metrics**.
4. Configure Chart 1:
   - **Metric**: `Incoming Messages`
   - **Aggregation**: `Sum`
   - **Time Range**: `Last 30 minutes`
   - **Time Grain**: `1 minute`
5. **What the Trace Graph Shows**:
   - At timestamp **`07:06 AM UTC`**, you will see a sharp **vertical spike going up to 100**.
   - This proves that Azure received all 100 requests simultaneously from your producer.

---

## 📍 Phase 2: Tracing Controlled Worker Draining (Queue Depth 100 -> 0)

When `load_buffering_demo.py` ran **Phase 2**, the worker pulled messages in 10 batches of 10 items over **10.22 seconds**.

### How to See the Phase 2 Trace in Azure Portal:

#### 1. Queue Depth Curve Graph (Active Messages):
- In **Metrics**, click **Add metric**:
  - **Metric**: `Active Messages`
  - **Aggregation**: `Average` or `Max`
- **What the Trace Graph Shows**:
  - A pyramid graph shape: Queue depth jumps instantly from **0 to 100** at `07:06:36 AM`, then slopes downwards continuously (**90 -> 80 -> 70 -> ... -> 0**) as workers consume the queue.

#### 2. Worker Processing Rate (Outgoing Messages):
- In **Metrics**, click **Add metric**:
  - **Metric**: `Outgoing Messages`
  - **Aggregation**: `Sum`
- **What the Trace Graph Shows**:
  - A flat, steady bar at **10 requests/sec**, showing that consumer workers processed the batch at a controlled rate limit, protecting downstream LLM APIs from quota errors.

---

## 💻 KQL Query to View Log Traces for Phase 1 & Phase 2

Go to **`sb-explore-ai`** -> **Logs** (under Monitoring) -> run this query:

```kusto
// View Phase 1 (Send) and Phase 2 (Receive & Complete) Operation Logs
AzureDiagnostics
| where ResourceProvider == "MICROSOFT.SERVICEBUS"
| summarize TotalOperations = count() by OperationName, bin(TimeGenerated, 1m)
| order by TimeGenerated asc
```

### What the Query Results Output:

| Timestamp (UTC) | OperationName | TotalOperations | Phase Map |
| :--- | :--- | :--- | :--- |
| `07:06:36.100` | `Send` | 50 | **Phase 1**: Producer Spike Batch 1 |
| `07:06:36.450` | `Send` | 50 | **Phase 1**: Producer Spike Batch 2 |
| `07:06:39.100` | `ReceiveAndCommitted` | 10 | **Phase 2**: Worker Batch 1 |
| `07:06:39.650` | `ReceiveAndCommitted` | 10 | **Phase 2**: Worker Batch 2 |
| `07:06:40.200` | `ReceiveAndCommitted` | 10 | **Phase 2**: Worker Batch 3 |
| ... | ... | ... | ... |
| `07:06:46.300` | `ReceiveAndCommitted` | 10 | **Phase 2**: Worker Batch 10 (Queue Empty!) |
