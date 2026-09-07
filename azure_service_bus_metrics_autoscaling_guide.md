# Azure Service Bus: Live Queue Metrics & KEDA Worker Auto-Scaling Guide

---

## 📈 Part 1: How to See Live Message Metrics & Traces in Azure

Azure Service Bus exposes 3 key operational metrics:
1. **Incoming Messages**: Rate of messages sent by producers.
2. **Active Messages (Queue Depth)**: Number of messages currently waiting in Azure memory/disk buffer.
3. **Outgoing Messages**: Rate of messages pulled and acknowledged by consumers.

---

### A. Live Azure Portal Metrics Dashboard (Visual Charts)

1. Open [Azure Portal](https://portal.azure.com/).
2. Go to **Resource groups** -> **`rg-explore-ai`** -> **`sb-explore-ai`** (Service Bus Namespace).
3. Click **Metrics** in the left sidebar menu (under *Monitoring*):
   - **Chart 1 (Incoming Rate)**: Metric = `Incoming Messages`, Aggregation = `Sum`.
   - **Chart 2 (Queue Depth)**: Metric = `Active Messages`, Aggregation = `Average`.
   - **Chart 3 (Outgoing Rate)**: Metric = `Outgoing Messages`, Aggregation = `Sum`.
4. Set Time range to **Last 30 minutes** with **1-minute granularity**.
5. You will see clear curve graphs showing when our script flooded 100 messages, how the queue depth spiked to 100, and how consumer workers drained it back down to 0!

---

### B. Live Azure CLI Polling Command

Run this command in PowerShell to poll live queue depth every 2 seconds:

```powershell
while ($true) {
    az servicebus queue show --resource-group rg-explore-ai --namespace-name sb-explore-ai --name ai-jobs-queue --query "{Active:countDetails.activeMessageCount, DeadLetter:countDetails.deadLetterMessageCount}" -o json
    Start-Sleep -Seconds 2
}
```

---

## ⚡ Part 2: How Auto-Scaling Works with Azure Service Bus (KEDA)

```
                                  +------------------------------------+
                                  |  Azure Service Bus Topic / Queue   |
                                  |   (Queue Depth: e.g. 250 Messages) |
                                  +------------------------------------+
                                                    |
                                                    | KEDA Scaler Monitors
                                                    | 'activeMessageCount'
                                                    v
                             +----------------------------------------------+
                             | KEDA Autoscaler (Azure Container Apps)       |
                             | Rule: 1 Worker per 10 Active Messages        |
                             +----------------------------------------------+
                                                    |
                                                    | Triggers Scale-Out
                                                    v
          +-----------------------------------------------------------------------------------+
          |  Worker Pool (Container Apps): Scales dynamically from 0 to 25 Container Replica Instances |
          |  [Worker 1]  [Worker 2]  [Worker 3]  ...  [Worker 25]                           |
          +-----------------------------------------------------------------------------------+
```

### Key Concept:
- **Service Bus itself**: Automatically scales internally to handle millions of messages without user intervention.
- **Worker Compute Auto-Scaling**: You scale your worker instances (Azure Container Apps / Azure Functions) based on **Queue Depth** (`activeMessageCount`) using **KEDA** (Kubernetes Event-driven Autoscaling).

---

### Real Azure Container Apps KEDA Autoscaler Config (Bicep/YAML)

In Azure Container Apps, you define a KEDA scaler connected to Service Bus:

```yaml
scale:
  minReplicas: 0    # Scales to 0 when queue is empty (Save 100% compute cost!)
  maxReplicas: 20   # Maximum worker containers during traffic spikes
  rules:
    - name: service-bus-queue-scaler
      custom:
        type: azure-servicebus
        metadata:
          queueName: ai-jobs-queue
          messageCount: "10"  # Target 10 active messages per worker container instance
        auth:
          - secretRef: sb-connection-string-secret
            triggerParameter: connection
```

> 💡 **How this Autoscales**:
> - If `activeMessages == 0` $\rightarrow$ Replicas = **0** (No active servers running, zero cost).
> - If `activeMessages == 50` $\rightarrow$ Replicas = $\frac{50}{10} =$ **5 Container Workers**.
> - If `activeMessages == 200` $\rightarrow$ Replicas = $\frac{200}{10} =$ **20 Container Workers** (Max limit).

---

## 🧪 Simulation Script: Live Auto-Scaler Simulation

In `service_bus_demo/`, we created a simulation script [simulate_keda_autoscaler.py](file:///c:/Users/2869026/Desktop/up/service_bus_demo/simulate_keda_autoscaler.py) that demonstrates KEDA autoscaling logic live in your terminal!
