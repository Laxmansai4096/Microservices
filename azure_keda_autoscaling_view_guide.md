# How to View & Monitor KEDA Auto-Scaling in Azure

---

## 🔍 Overview: How KEDA Auto-Scaling Works in Azure

When building microservices on **Azure Container Apps** (or Azure Kubernetes Service), **KEDA** (Kubernetes Event-driven Autoscaling) automatically polls your **Azure Service Bus Queue** depth (`activeMessageCount`).

```
+------------------------------------+
|  Azure Service Bus Queue           |
|  (Active Messages: e.g. 50 msgs)   |
+------------------------------------+
                  |
                  | KEDA Poller (Every 15s)
                  v
+-------------------------------------------------------------+
| Azure Container App (KEDA Scaler: 10 msgs per replica)      |
| 1. Queue Depth = 50 -> Scaled OUT to 5 Container Replicas   |
| 2. Queue Depth =  0 -> Scaled IN to 0 Replicas (Zero Cost!) |
+-------------------------------------------------------------+
```

---

## 📍 1. View KEDA Auto-Scaling in Azure Portal

### Step A: Inspect the KEDA Scale Rule & Live Replicas
1. Open [Azure Portal](https://portal.azure.com/).
2. Search for **Container Apps** -> select your worker container app (e.g. `ca-ai-worker`).
3. In the left menu under **Application**, click **Scale**:
   - **Min Replicas**: `0` *(Zero cost when idle)*
   - **Max Replicas**: `10`
   - **Scale Rules Table**:
     - **Rule Name**: `service-bus-queue-scaler`
     - **Type**: `Custom`
     - **Metadata**: `queueName: ai-jobs-queue`, `messageCount: 10`

---

### Step B: View Live Replica Count Chart (Scale-Out & Scale-In Graph)

1. In your Container App menu (under **Monitoring**), click **Metrics**.
2. Select:
   - **Metric**: `Replica Count`
   - **Aggregation**: `Max` or `Average`
   - **Time Range**: `Last 30 minutes`
3. **What the Graph Shows**:
   - When no messages are in Service Bus: **Replica Count = 0** (Flat baseline).
   - When 100 messages enter Service Bus: **Replica Count jumps to 10** (Step-up scale-out curve).
   - As workers process messages and queue reaches 0: **Replica Count drops back to 0** (Scale-to-zero).

---

## 📍 2. View KEDA Auto-Scaling via Azure CLI

### A. List Live Running Worker Container Instances
```bash
az containerapp replica list \
  --resource-group rg-explore-ai \
  --name ca-ai-worker \
  -o table
```
*Output when active:* Shows list of running container replica IDs (`ca-ai-worker--xyz-replica-1`, `ca-ai-worker--xyz-replica-2`, etc.).

---

### B. Stream Live KEDA System Scaling Logs
```bash
az containerapp logs show \
  --resource-group rg-explore-ai \
  --name ca-ai-worker \
  --type system \
  --follow
```
*Output Logs:* Shows KEDA scale events such as:
`KEDA: Scaling container app 'ca-ai-worker' from 0 to 5 replicas due to 50 active messages in queue 'ai-jobs-queue'.`

---

## 📍 3. Query KEDA Scaling Logs in Log Analytics (KQL)

Go to your **Log Analytics Workspace** -> **Logs** -> paste this KQL query:

```kusto
// Query KEDA Scaling Decision Logs
ContainerAppSystemLogs_CL
| where Log_s contains "scale" or Log_s contains "replica" or Log_s contains "keda"
| project TimeGenerated, ContainerAppName_s, Log_s
| order by TimeGenerated desc
```

---

## 🧪 How to Trigger & Observe a Live KEDA Scale Event

1. **Start Live Monitoring** in Terminal 1:
   ```bash
   az containerapp replica list --resource-group rg-explore-ai --name ca-ai-worker -o table
   ```
2. **Flood 100 Messages** into Azure Service Bus in Terminal 2:
   ```bash
   cd c:\Users\2869026\Desktop\up\service_bus_demo
   python load_buffering_demo.py
   ```
3. **Observe KEDA Action**:
   - Within 15 seconds, KEDA detects 100 active messages in Service Bus.
   - Azure Container Apps automatically provisions **10 new container replicas** to process the queue in parallel.
   - Once completed, KEDA automatically shuts down all containers back to **0 replicas**.
