# Azure Service Bus: Complete Guide to Viewing Message & Operational Traces

---

## 🔍 How Message Tracing Works in Azure Service Bus

When a **Producer** sends a message or a **Consumer** processes/locks/completes a message, Azure provides 3 main mechanisms to view traces:

1. **Service Bus Explorer (State & Content Traces)**: Inspect payload, system headers (`MessageId`, `SequenceNumber`, `EnqueuedTimeUtc`), custom headers, and Dead-Letter reasons.
2. **Azure Log Analytics / Diagnostic Logs (Operational API Traces)**: KQL queries showing every `Send`, `Receive`, `Complete`, `Abandon`, and `DeadLetter` API call with timestamps and caller IP.
3. **Application Insights / OpenTelemetry (End-to-End Distributed Tracing)**: W3C trace propagation linking Producer web request -> Service Bus message -> Consumer worker execution.

---

## 📍 Method 1: Inspect Message Traces via Service Bus Explorer (Portal)

This is the fastest visual way to see individual messages sent by your producer or sitting in the queue.

### Steps to View Sent Message Traces:
1. Go to **Azure Portal** -> **Resource groups** -> **`rg-explore-ai`** -> **`sb-explore-ai`**.
2. Click **Queues** -> **`ai-jobs-queue`**.
3. Click **Service Bus Explorer** in the left menu.
4. Click the **Peek** tab at the top:
   - Select **Queue type**: *Main queue* (or *Dead-letter queue*).
   - Set **Mode**: *Peek from start*.
   - Set **Max message count**: `32`.
   - Click **Peek**.
5. Click on any message in the list to open its **Trace Details Panel**:

#### What You Will See in the Trace Panel:

| Trace Field | Description & Example |
| :--- | :--- |
| **Sequence Number** | Unique incremental integer assigned by Azure when producer enqueues (`1`, `2`, `3`). |
| **Message ID** | Producer-defined or auto-generated GUID (`job-rag-9faa06`). |
| **Enqueued Time UTC** | Exact millisecond timestamp when Azure received the message. |
| **Size (Bytes)** | Exact payload byte size (e.g. `245 B`). |
| **Delivery Count** | Number of times a consumer has attempted to process this message (`0` = new, `1+` = retried). |
| **Custom Properties** | Application headers passed by producer (`model: gpt-4o`, `priority: HIGH`). |
| **Message Body** | Full JSON / binary payload sent by producer. |

---

## 📍 Method 2: Inspect Consumer Failure & DLQ Traces

When a consumer fails or dead-letters a message, Azure records specific error telemetry.

### Steps to View Consumer Failure Traces:
1. In **Service Bus Explorer**, set **Queue type** to **Dead-letter queue**.
2. Click **Peek from start** -> select a dead-lettered message (`job-corrupt-a20ccc`).
3. Expand **System Properties** on the right side:

```json
{
  "DeadLetterReason": "UnreadableDocumentFormat",
  "DeadLetterErrorDescription": "File header corrupted or password protected.",
  "DeliveryCount": 2,
  "EnqueuedSequenceNumber": 14,
  "DeadLetteringSource": "ai-jobs-queue"
}
```

> 💡 **Key Insight**: The `DeadLetterReason` and `DeadLetterErrorDescription` tell you *exactly why* the consumer rejected the message.

---

## 📍 Method 3: Operational API Traces via Log Analytics (KQL Queries)

If you enable **Diagnostic Settings** on your Service Bus namespace, Azure logs every single `Send`, `Receive`, `Complete`, `Abandon`, and `DeadLetter` operation into a Log Analytics Workspace.

### 1. Diagnostic Logging Status (Active in your Azure Account)

> ℹ️ **Status**: Diagnostic logging is **ALREADY ACTIVE** on your Service Bus namespace `sb-explore-ai` connected to Log Analytics Workspace `workspace-rgexploreaiF1lX`.

If you ever need to create or re-create a diagnostic setting in PowerShell, use a single-line command (avoiding Linux `\` continuation lines):

```powershell
az monitor diagnostic-settings create --resource "/subscriptions/6fb67c72-73dc-4767-a210-0ea6b6c99feb/resourceGroups/rg-explore-ai/providers/Microsoft.ServiceBus/namespaces/sb-explore-ai" --name "sb-operation-traces" --workspace "/subscriptions/6fb67c72-73dc-4767-a210-0ea6b6c99feb/resourceGroups/rg-explore-ai/providers/Microsoft.OperationalInsights/workspaces/workspace-rgexploreaiF1lX" --logs '[{"category":"RuntimeAuditLogs","enabled":true},{"category":"ApplicationMetricsLogs","enabled":true}]'
```

### 2. Query Operational Traces with Kusto (KQL) in Azure Portal:
Go to **`sb-explore-ai`** -> **Logs** (under Monitoring) -> paste this KQL query:

```kusto
// View all Producer (Send) and Consumer (Receive/Complete) API Traces
AzureDiagnostics
| where ResourceProvider == "MICROSOFT.SERVICEBUS"
| project TimeGenerated, OperationName, Category, Resource, Status, CallerIpAddress
| order by TimeGenerated desc
```

#### What this KQL Query Traces:
- `Send`: Shows when `producer.py` enqueued messages.
- `Receive` / `ReceiveAndCommitted`: Shows when `consumer.py` pulled messages.
- `Complete`: Shows when consumer acknowledged successful processing.
- `Abandon`: Shows when consumer failed and released lock for retry.
- `DeadLetter`: Shows when message was moved to DLQ.

---

## 📍 Method 4: End-to-End Distributed Tracing (Application Insights)

When building real AI microservices, Python `azure-servicebus` automatically injects **W3C Trace Context headers** into message properties:

```json
"application_properties": {
  "traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
  "tracestate": "rojo=1"
}
```

### How End-to-End Tracing Works:
1. **User HTTP Request**: Web App receives prompt (Trace ID: `4bf92f35...`).
2. **Producer Enqueue**: Producer injects `traceparent` into Service Bus message headers.
3. **Consumer Background Worker**: Consumer reads `traceparent` header and inherits the SAME Trace ID.
4. **Application Insights Transaction Map**: Go to **Application Insights** -> **Transaction Search** -> search for Trace ID `4bf92f35...`.
   - Azure displays a **single visual timeline**:
     `User HTTP Post` -> `Service Bus Queue (ai-jobs-queue)` -> `Consumer Worker` -> `Azure OpenAI API Call`!
