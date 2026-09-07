# Azure Container Registry (ACR): Master Guide for AI & Cloud Engineers

## 1. What is Azure Container Registry (ACR)?
**Azure Container Registry (ACR)** is a managed, private Docker registry service based on the open-source OCI (Open Container Initiative) distribution specification. It allows you to build, store, and manage container images and artifacts across all types of container deployments in Azure (Azure Container Apps, Azure Kubernetes Service, Azure Functions, Azure Web Apps).

---

## 2. Core Concepts & Architecture

| Concept | Description |
| :--- | :--- |
| **Login Server** | The unique FQDN URL for your private registry (`<registry_name>.azurecr.io`). |
| **Repository** | A collection of container images with the same name, categorized by tags (e.g. `ai-agent-service`). |
| **Tag & Digest** | **Tag**: Human-readable version label (`v1.0`, `latest`). **Digest**: Immutable SHA-256 hash identifying the exact image build. |
| **ACR Tasks (`az acr build`)** | Cloud-native build service that builds Docker images directly in Azure **without requiring Docker Desktop on your local machine**! |
| **Authentication & RBAC** | Access control via **Microsoft Entra ID Managed Identity** with roles: `AcrPull` (Read/Pull), `AcrPush` (Write/Push), `AcrDelete`, or Admin Access Keys. |

---

## 3. Full Feature Breakdown

### A. Cloud-Native Image Building (`az acr build`)
- Eliminates the need for local Docker engines.
- Uploads your source code context to Azure and executes the Docker build natively in cloud compute.

### B. Registry Tiers & Capabilities

| Feature | Basic SKU | Standard SKU | Premium SKU |
| :--- | :--- | :--- | :--- |
| **Included Storage** | 10 GB | 100 GB | 500 GB |
| **Read/Write Operations** | High | Higher | Ultra High |
| **Geo-Replication** | ❌ | ❌ | ✅ (Replicate across multiple Azure regions) |
| **Private Endpoints & VNet** | ❌ | ❌ | ✅ (Secure private network isolation) |
| **Content Trust (Signing)** | ❌ | ❌ | ✅ (Digital signature verification) |

### C. Webhooks & CI/CD Integration
- Send HTTP webhooks when new container tags are pushed.
- Triggers automatic container app deployment in Azure Container Apps or AKS.

---

## 4. Why ACR is Essential for AI Engineers

1. **Packaging Heavy AI Dependencies**:
   - AI frameworks (PyTorch, TensorFlow, Transformers, CUDA drivers, vLLM) have huge multi-gigabyte dependency trees.
   - ACR stores these layers in private, high-bandwidth storage right next to your Azure compute, ensuring sub-second container pulls.
2. **Docker-less Builds for AI Workspaces**:
   - Developers working on constrained machines can build 5GB+ AI Docker images in the cloud using `az acr build`.
3. **Secure Proprietary Model Storage**:
   - Custom fine-tuned LLM weights and private AI agent algorithms remain strictly isolated within your private Azure tenant.
4. **Seamless Integration with Azure Container Apps (ACA)**:
   - ACA pulls images directly from ACR using passwordless Managed Identity (`AcrPull`).

---

## 5. Live Azure CLI & Portal Exploration Guide

### Step 1: Check Existing ACR Resource in Resource Group `rg-explore-ai`
```bash
az acr list --resource-group rg-explore-ai -o table
```
*Existing Registry Name*: `acrexploreai65064`  
*Login Server*: `acrexploreai65064.azurecr.io`

### Step 2: Build & Push a Container Image to ACR (Cloud Build)
```bash
cd c:\Users\2869026\Desktop\up\acr_ai_demo

# Build container natively in Azure Cloud
az acr build \
  --registry acrexploreai65064 \
  --image ai-microservice:v1 .
```

### Step 3: Inspect Repositories & Tags in Azure CLI
```bash
# List repositories
az acr repository list --name acrexploreai65064 -o table

# List tags for image
az acr repository show-tags --name acrexploreai65064 --repository ai-microservice -o table
```

### Step 4: Explore in Azure Portal UI
1. Go to **Azure Portal** -> **`rg-explore-ai`** -> **`acrexploreai65064`** (Container registry).
2. Click **Repositories** in the left menu.
3. Click on **`ai-microservice`** -> Tag **`v1`**:
   - Inspect **Digest SHA256**, **Created Time**, **Manifest JSON**, and **Layer details**.
