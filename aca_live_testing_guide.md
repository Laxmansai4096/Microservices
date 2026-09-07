# Hands-On Azure Container Apps (ACA) Feature Testing & Learning Guide

This document provides an interactive, feature-by-feature testing laboratory for **Azure Container Apps (ACA)**. Each section breaks down:
1. **What the feature is and how it works**
2. **Why it is useful for real-world AI microservices**
3. **Pros and Cons of the feature**
4. **Step-by-step terminal commands to test and observe the feature live** in your Azure environment (`rg-explore-ai` / `cae-explore-ai`).

---

## Interactive Feature Index
- [Feature 1: HTTP Ingress & External FQDN Routing](#feature-1-http-ingress--external-fqdn-routing)
- [Feature 2: Scale-to-Zero (`minReplicas = 0`) & Cold Start](#feature-2-scale-to-zero-minreplicas--0--cold-start)
- [Feature 3: Warm Provisioned Instances (`minReplicas = 1`)](#feature-3-warm-provisioned-instances-minreplicas--1)
- [Feature 4: Horizontal KEDA Autoscaling under Load](#feature-4-horizontal-keda-autoscaling-under-load)
- [Feature 5: Immutable Revisions & Environment Variables](#feature-5-immutable-revisions--environment-variables)
- [Feature 6: Traffic Splitting & Canary Deployments](#feature-6-traffic-splitting--canary-deployments)
- [Feature 7: Real-Time Container Log Streaming](#feature-7-real-time-container-log-streaming)
- [Feature 8: ACA Jobs (Ephemeral Batch Workloads)](#feature-8-aca-jobs-ephemeral-batch-workloads)
- [Feature 9: Managed Identity & Passwordless Authentication](#feature-9-managed-identity--passwordless-authentication)

---

## Feature 1: HTTP Ingress & External FQDN Routing

### What It Does
ACA provides built-in **Envoy Proxy** edge routing. When enabled, ACA automatically assigns a public Fully Qualified Domain Name (FQDN) with managed TLS/SSL certificates and routes incoming HTTP/HTTPS requests on your designated target port (e.g. 80 or 8000) directly to active container replicas.

### Why It Is Useful
- Eliminates the need to install or configure custom NGINX ingress controllers, reverse proxies, or cloud load balancers.
- Provides secure HTTPS endpoints out of the box for client web apps, mobile apps, or webhooks calling your AI REST APIs.

### Pros & Cons
- **Pros**: Free managed SSL certificates, automatic DNS mapping, support for HTTP/1.1, HTTP/2, WebSockets, and gRPC streaming.
- **Cons**: Only one target port per container app can be exposed for ingress traffic.

### Step-by-Step Live Test

#### Step 1: Query the App Ingress Configuration
```bash
az containerapp show \
  --name aca-ai-agent \
  --resource-group rg-explore-ai \
  --query "properties.configuration.ingress" \
  --output json
```

#### Step 2: Test Live Endpoint over Public HTTPS
```powershell
Invoke-RestMethod -Uri "https://aca-ai-agent.yellowwater-c3bd8780.eastus.azurecontainerapps.io/" -Method Get
```

#### Expected Result
Returns HTTP Status 200 with HTML/JSON content from the live container app instance.

---

## Feature 2: Scale-to-Zero (`minReplicas = 0`) & Cold Start

### What It Does
When no HTTP requests arrive within the cooldown period (default 300 seconds), KEDA scales the number of active container instances down to **0**. When a new HTTP request hits the Envoy ingress, ACA automatically boots up a container instance to process the request.

### Why It Is Useful
- **100% Compute Savings**: You pay strictly **$0.00** for vCPU and RAM when your application is idle (e.g. during night hours or weekends).

### Pros & Cons
- **Pros**: Dramatic cost reduction for non-24/7 workloads, dev/test environments, or internal batch tools.
- **Cons**: **Cold Start Latency** — The very first user request must wait 5 to 15 seconds for container initialization, image pull, and framework startup.

### Step-by-Step Live Test

#### Step 1: Configure App to Scale to Zero
```bash
az containerapp update \
  --name aca-ai-agent \
  --resource-group rg-explore-ai \
  --min-replicas 0 \
  --max-replicas 5
```

#### Step 2: Observe Active Replicas Scale Down to 0
Wait 3–5 minutes without sending traffic, then run:
```bash
az containerapp revision list \
  --name aca-ai-agent \
  --resource-group rg-explore-ai \
  --output table
```

#### Step 3: Trigger Cold Start
Send a new HTTP request and measure response time:
```powershell
Measure-Command { Invoke-RestMethod -Uri "https://aca-ai-agent.yellowwater-c3bd8780.eastus.azurecontainerapps.io/" }
```

#### Expected Result
`Replicas` count in `revision list` will show `0` when idle, then increment to `1` upon receiving the request, with the request taking ~5-8 seconds due to cold start container boot.

---

## Feature 3: Warm Provisioned Instances (`minReplicas = 1`)

### What It Does
Setting `minReplicas = 1` guarantees that at least one container instance stays booted and ready in memory 24/7, even when zero traffic is arriving.

### Why It Is Useful
- Completely **eliminates cold start delays** for production AI chatbots, user-facing search APIs, and SLA-bound microservices.

### Pros & Cons
- **Pros**: Sub-second API response times; predictable low latency for all users.
- **Cons**: Incurs continuous billing for 1 base vCPU/RAM allocation 24/7.

### Step-by-Step Live Test

#### Step 1: Update App to Maintain 1 Warm Instance
```bash
az containerapp update \
  --name aca-ai-agent \
  --resource-group rg-explore-ai \
  --min-replicas 1 \
  --max-replicas 5
```

#### Step 2: Verify Instant Response Time
```powershell
Measure-Command { Invoke-RestMethod -Uri "https://aca-ai-agent.yellowwater-c3bd8780.eastus.azurecontainerapps.io/" }
```

#### Expected Result
Execution time drops from ~5-8 seconds down to **< 300 milliseconds**.

---

## Feature 4: Horizontal KEDA Autoscaling under Load

### What It Does
ACA monitors incoming HTTP request concurrency or custom metric rules. When traffic spikes beyond your defined threshold, KEDA automatically spins up additional container replicas (up to `maxReplicas`).

### Why It Is Useful
- Prevents service crashes during sudden traffic spikes (e.g. 50 users simultaneously requesting heavy LLM prompt completions).

### Pros & Cons
- **Pros**: Automatic elastic scaling up and down; protects service availability under load.
- **Cons**: Applications must be **stateless** so any replica can handle any user request.

### Step-by-Step Live Test

#### Step 1: Add an HTTP Concurrency Scale Rule (Target: 3 Concurrent Requests)
```bash
az containerapp update \
  --name aca-ai-agent \
  --resource-group rg-explore-ai \
  --scale-rule-name http-rule \
  --scale-rule-type http \
  --scale-rule-metadata concurrentRequests=3
```

#### Step 2: Inspect Scaled Replicas
```bash
az containerapp replica list \
  --name aca-ai-agent \
  --resource-group rg-explore-ai \
  --output table
```

---

## Feature 5: Immutable Revisions & Environment Variables

### What It Does
Every change to environment variables, container image, or scale settings creates a new, immutable snapshot called a **Revision**.

### Why It Is Useful
- Provides full revision history and auditing. You can update configuration parameters (like system prompts, model endpoints, or API keys) safely without touching running code.

### Pros & Cons
- **Pros**: Immutable state management, seamless rollback capability.
- **Cons**: Multiple old inactive revisions can accumulate over time (can be cleaned up/deactivated).

### Step-by-Step Live Test

#### Step 1: Set an Environment Variable (Creates a New Revision)
```bash
az containerapp update \
  --name aca-ai-agent \
  --resource-group rg-explore-ai \
  --set-env-vars AI_MODEL_VERSION="gpt-4o-v2" SYSTEM_PROMPT="You are a helpful assistant."
```

#### Step 2: List Revisions to See the Newly Generated Revision
```bash
az containerapp revision list \
  --name aca-ai-agent \
  --resource-group rg-explore-ai \
  --output table
```

#### Expected Result
You will see two revisions listed (e.g., `aca-ai-agent--old` and `aca-ai-agent--new`), with 100% of traffic automatically directed to the newest provisioned revision.

---

## Feature 6: Traffic Splitting & Canary Deployments

### What It Does
In **Multiple Revision Mode**, ACA allows you to split incoming HTTP traffic across multiple active revisions by exact percentage weights (e.g. 80% / 20%).

### Why It Is Useful
- **Canary Testing**: Safely test a new AI prompt version or model update on 10% of live traffic before rolling out to 100% of users.
- **Instant Rollback**: If the new revision displays errors, route 100% of traffic back to the previous revision instantly without rebuilding code.

### Pros & Cons
- **Pros**: Zero-downtime prompt engineering & model A/B testing in live production.
- **Cons**: Client sessions must tolerate receiving responses from either revision unless session affinity is configured.

### Step-by-Step Live Test

#### Step 1: Enable Multiple Revision Mode
```bash
az containerapp update \
  --name aca-ai-agent \
  --resource-group rg-explore-ai \
  --revision-suffix v2
```

#### Step 2: Split Ingress Traffic (80% to Original, 20% to Latest v2)
```bash
# Obtain revision names from: az containerapp revision list -g rg-explore-ai --name aca-ai-agent
az containerapp ingress traffic set \
  --name aca-ai-agent \
  --resource-group rg-explore-ai \
  --revision-weight LATEST=20 aca-ai-agent--be051bf=80
```

#### Step 3: Verify Traffic Split Allocation
```bash
az containerapp show \
  --name aca-ai-agent \
  --resource-group rg-explore-ai \
  --query "properties.configuration.ingress.traffic" \
  --output json
```

#### Expected Result
Returns JSON array showing `weight: 80` for revision 1 and `weight: 20` for revision 2.

---

## Feature 7: Real-Time Container Log Streaming

### What It Does
Streams standard output (`stdout`) and standard error (`stderr`) logs directly from running container replicas in real time over CLI or Azure Portal.

### Why It Is Useful
- Essential for real-time debugging, tracing AI model prompt execution, monitoring API exceptions, and checking initialization status.

### Pros & Cons
- **Pros**: Immediate debugging feedback without needing SSH/terminal access inside pod containers.
- **Cons**: High log output volumes can overflow CLI buffers (use Log Analytics for historical queries).

### Step-by-Step Live Test

#### Stream Live Logs from Terminal
```bash
az containerapp logs show \
  --name aca-ai-agent \
  --resource-group rg-explore-ai \
  --follow
```

#### Expected Result
Terminal displays live log output from the container, updating instantly when requests arrive.

---

## Feature 8: ACA Jobs (Ephemeral Batch Workloads)

### What It Does
Unlike continuous Container Apps, **ACA Jobs** run ephemeral container tasks that execute to completion and exit.

### Why It Is Useful
- Perfect for nightly vector database re-indexing, batch LLM evaluations, automated data transformation scripts, or model fine-tuning runs.

### Pros & Cons
- **Pros**: Billing stops immediately when the job finishes executing; no idle memory cost.
- **Cons**: Not designed for serving HTTP web traffic or persistent API connections.

### Step-by-Step Live Test

#### Step 1: Create an Ephemeral ACA Job
```bash
az containerapp job create \
  --name aca-batch-job \
  --resource-group rg-explore-ai \
  --environment cae-explore-ai \
  --trigger-type Manual \
  --replica-timeout 1800 \
  --replica-retry-limit 1 \
  --image mcr.microsoft.com/k8se/quickstart:latest \
  --cpu "0.25" --memory "0.5Gi"
```

#### Step 2: Trigger Manual Execution
```bash
az containerapp job start \
  --name aca-batch-job \
  --resource-group rg-explore-ai
```

#### Step 3: Check Job Execution History
```bash
az containerapp job execution list \
  --name aca-batch-job \
  --resource-group rg-explore-ai \
  --output table
```

#### Expected Result
Execution status will show `Running` -> `Succeeded` -> `Terminated`.

---

## Feature 9: Managed Identity & Passwordless Authentication

### What It Does
Assigns an **Azure Entra ID (Azure AD) Managed Identity** to the Container App, allowing it to authenticate with Azure Services (ACR, Key Vault, AI Services, Blob Storage) without embedding client secrets or passwords in code.

### Why It Is Useful
- Enterprise-grade security compliance; eliminates hardcoded API keys and credentials from source control.

### Pros & Cons
- **Pros**: Passwordless, zero secret management overhead, automatic token rotation.
- **Cons**: Requires role assignments (RBAC) configured on target Azure resources.

### Step-by-Step Live Test

#### Assign System Identity to Container App
```bash
az containerapp identity assign \
  --name aca-ai-agent \
  --resource-group rg-explore-ai \
  --system-assigned
```

#### Expected Result
Returns `principalId` and `tenantId` representing the identity of `aca-ai-agent` in Azure Active Directory.

---

## Feature Summary Reference Matrix

| Feature | Primary Purpose | Best AI / Microservice Use Case | Cost Impact |
| :--- | :--- | :--- | :--- |
| **HTTP Ingress** | External URL + TLS termination | REST APIs, Streamlit UIs | Free built-in feature |
| **Scale to Zero** | Shutdown when idle | Dev/test APIs, internal tools | **$0 when idle** |
| **Min Replicas = 1** | Warm instance 24/7 | Production latency-sensitive APIs | Continuous vCPU/RAM base |
| **KEDA Autoscaling** | Elastic scale under load | Burst handling for high LLM traffic | Scales dynamically with traffic |
| **Revisions** | Immutable snapshot tracking | Zero-downtime deployment & rollbacks | Included |
| **Traffic Splitting** | Percentage traffic distribution | Prompt engineering A/B testing | Included |
| **Live Log Streaming** | Real-time stdout streaming | Real-time debugging & prompt tracing | Included |
| **ACA Jobs** | Ephemeral batch executions | Nightly vector index sync | Pays only while executing |
| **Managed Identity** | Passwordless authentication | Secure connection to Key Vault & AI Services | Free built-in feature |
