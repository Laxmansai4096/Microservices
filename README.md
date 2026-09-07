# 📘 Azure Microservices Master Handbook for AI Engineers

Welcome to the **Master Architecture & Feature Reference Notes for Azure Microservices**. This repository contains dedicated, feature-by-feature master notes, real-world AI use cases, pros & cons, and end-to-end Azure CLI/Portal execution steps for each pillar of Azure Microservices.

---

## 🏛️ Architecture Blueprint & Navigation

```
                                  +------------------------------------+
                                  |   Azure Container Registry (ACR)   |
                                  |   (Private AI Docker Images)       |
                                  +------------------------------------+
                                                    |
                                                    v Image Pull
+------------------+      Publish Job    +------------------------------------+      KEDA Scale     +------------------------------------+
|  Fast API / Web  | ------------------> |     Azure Service Bus Queue        | ------------------> |  Azure Container Apps (ACA) Pool   |
|  (User Interface)| <--- 202 Accepted - |  (Rate Limit Buffer & DLQ Retry)   |                     |  (Parallel LLM & RAG Workers)      |
+------------------+                     +------------------------------------+                     +------------------------------------+
                                                    |                                                                 |
                                                    v Event Trigger                                                   v API Call
                                         +------------------------------------+                             +------------------------------------+
                                         |    Azure Functions (Serverless)    |                             |      Azure OpenAI / Vector DB      |
                                         |  (Lightweight Pipelines / Cron)    |                             +------------------------------------+
                                         +------------------------------------+
```

---

## 📂 Master Notes Navigation

### 1. 🏛️ [Azure Container Apps (ACA)](file:///c:/Users/2869026/Desktop/up/azure_container_apps/azure_container_apps_master_notes.md)
- **Master Notes File**: [`azure_container_apps/azure_container_apps_master_notes.md`](file:///c:/Users/2869026/Desktop/up/azure_container_apps/azure_container_apps_master_notes.md)
- **Coverage**: Scale-to-Zero, KEDA Autoscaling, Revision Management (A/B Testing), Dapr Integration, Managed Ingress, Pros & Cons, End-to-End Azure CLI/Portal steps.

### 2. ⚡ [Azure Functions (Serverless FaaS)](file:///c:/Users/2869026/Desktop/up/azure_functions/azure_functions_master_notes.md)
- **Master Notes File**: [`azure_functions/azure_functions_master_notes.md`](file:///c:/Users/2869026/Desktop/up/azure_functions/azure_functions_master_notes.md)
- **Coverage**: Event-Driven Triggers (`BlobTrigger`, `ServiceBusTrigger`), Input/Output Bindings, Premium Elastic Scale (Zero Cold-Start), Custom Docker Containers, Pros & Cons, Azure CLI/Portal steps.

### 3. 📬 [Azure Service Bus (Enterprise Messaging)](file:///c:/Users/2869026/Desktop/up/azure_service_bus/azure_service_bus_master_notes.md)
- **Master Notes File**: [`azure_service_bus/azure_service_bus_master_notes.md`](file:///c:/Users/2869026/Desktop/up/azure_service_bus/azure_service_bus_master_notes.md)
- **Coverage**: Rate-Limit Buffering (OpenAI HTTP 429 quota protection), Peek-Lock delivery, Dead-Letter Queue (DLQ), Pub/Sub Topics & SQL Rules, FIFO Message Sessions, Pros & Cons, Azure CLI/Portal steps.

### 4. 📦 [Azure Container Registry (ACR)](file:///c:/Users/2869026/Desktop/up/azure_container_registry/azure_container_registry_master_notes.md)
- **Master Notes File**: [`azure_container_registry/azure_container_registry_master_notes.md`](file:///c:/Users/2869026/Desktop/up/azure_container_registry/azure_container_registry_master_notes.md)
- **Coverage**: Private OCI Repositories, Passwordless Managed Identity Auth (`AcrPull`), Cloud-Native Building (`az acr build`), Webhooks, Security Scanning (Microsoft Defender), Scope Maps/Tokens, Pros & Cons, Azure CLI/Portal steps.

---

## 📑 Microservices Comparison Matrix

| Microservice Pillar | Primary Architectural Role | Scale Mechanism | Key Advantage for AI Systems |
| :--- | :--- | :--- | :--- |
| **Azure Container Apps (ACA)** | Long-running microservices, APIs & LLM Inference Workers | KEDA (0 to N Replicas based on HTTP / Queue Depth) | Serverless container execution with zero-cost idle scaling |
| **Azure Functions** | Short-lived, event-driven pipelines & cron triggers | Event-Driven Elastic Scale (Pre-warmed instances) | Instant event execution on Blob/Service Bus events with 0 boilerplate |
| **Azure Service Bus** | Asynchronous messaging, rate-limit buffer & agent pub/sub | Managed PaaS Infrastructure (Millions of msgs/sec) | Decouples web apps from LLMs, protects against HTTP 429 rate limits |
| **Azure Container Registry (ACR)** | Private container storage & cloud container builds | Cloud Storage (10 GB to 500 GB+) | Secure storage for PyTorch/CUDA images & fine-tuned model code |
