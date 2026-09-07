# Azure Service Bus Auto-Scaling vs. Worker Container Auto-Scaling

---

## 💡 Clarifying the Two Types of Auto-Scaling

When traffic surges, two distinct types of auto-scaling happen in Azure:

```
[1000 User Traffic Surge]
           |
           v
+-----------------------------------------------------------------------+
| TYPE 1: Azure Service Bus Namespace (PaaS Managed Infrastructure)     |
| - Automatically scales internal broker capacity & bandwidth          |
| - Holds 1,000+ messages in a single queue without crashing           |
| - Metric to verify: 'Throttled Requests' = 0                         |
+-----------------------------------------------------------------------+
                                   |
                                   | KEDA Monitors Queue Depth
                                   v
+-----------------------------------------------------------------------+
| TYPE 2: Worker App Replicas (Azure Container Apps / KEDA)             |
| - Scales compute worker instances from 1 container -> 10 containers    |
| - Drains the 1,000 messages in parallel 10x faster                    |
| - Metric to verify: 'Replica Count' = 10                              |
+-----------------------------------------------------------------------+
```

---

## 📈 1. How to See Azure Service Bus Capacity Auto-Scaling (Type 1)

Because Azure Service Bus is a **fully managed serverless service**, you do not create multiple Service Bus resources. Instead, Azure automatically scales the underlying compute nodes of your single namespace (`sb-explore-ai`).

### How to Verify Service Bus Scaled Capacity in Azure Portal:

1. Go to [Azure Portal](https://portal.azure.com/) -> **`rg-explore-ai`** -> **`sb-explore-ai`** (Service Bus Namespace).
2. Click **Metrics** in the left menu (under *Monitoring*):
   - **Chart 1: `Successful Requests`** (Aggregation: `Sum`)
     - *What it shows*: Spikes up to 100+ requests in seconds, proving Azure Service Bus instantly expanded connection handling.
   - **Chart 2: `Throttled Requests`** (Aggregation: `Sum`)
     - *What it shows*: If **`Throttled Requests = 0`**, it proves Service Bus successfully scaled its internal processing capacity without rejecting a single request!
   - **Chart 3: `Active Messages`** (Aggregation: `Max`)
     - *What it shows*: Service Bus expanded its queue buffer storage dynamically to hold all incoming messages.

---

## ⚡ 2. How to See Worker Container Auto-Scaling (Type 2 - KEDA)

KEDA does not create more Service Bus queues; it creates **more worker container instances (replicas)** to process the messages inside the queue in parallel.

### How to Verify Worker Container Scaling in Azure Portal:

1. Go to **Azure Portal** -> **Container Apps** -> select your worker app (e.g. `ca-ai-worker`).
2. Click **Metrics** -> select **`Replica Count`**:
   - When traffic is zero: **Replica Count = 0**
   - When 100 messages arrive: **Replica Count = 10** (10 container instances running in parallel!)
3. Click **Scale** in the left menu to view your active KEDA rule:
   - Metadata: `queueName: ai-jobs-queue`, `messageCount: 10`.
