# 📦 Azure Container Registry (ACR): Master Notes for AI Engineers

---

## 📖 1. What is Azure Container Registry?
**Azure Container Registry (ACR)** is a managed, private OCI (Open Container Initiative) Docker registry hosted within Azure for building, storing, securing, and replicating container images and AI model artifacts.

---

## ⚡ 2. Core Features & Functionalities

### Feature 1: Private OCI Repositories & Immutable Tagging
- **Functionality**: Stores Docker images organized by repository name (`ai-service`) and version tags (`v1.0`, `latest`) or SHA-256 digests.
- **Importance for AI Engineers**: Protects proprietary fine-tuned model weights and algorithms from public exposure. Guarantees 100% reproducible builds.
- **Real-World Example**: Deploy `ai-agent:v1.0` to production. If an issue occurs, instantly roll back to exact digest `ai-agent@sha256:8f3a...`.

### Feature 2: Passwordless Auth via Managed Identity (`AcrPull` / `AcrPush`)
- **Functionality**: Authenticates Azure Container Apps and AKS to ACR using Entra ID RBAC roles (`AcrPull` / `AcrPush`).
- **Importance for AI Engineers**: Eliminates hardcoded passwords or secret keys in source code or `.env` files.
- **Real-World Example**: ACA pulls heavy 5GB AI Docker images from ACR securely using its System-Assigned Identity without storing registry credentials.

### Feature 3: Cloud-Native Container Building (`az acr build`)
- **Functionality**: Offloads Docker image building to Azure cloud servers without requiring Docker Desktop on developer machines.
- **Importance for AI Engineers**: Allows AI engineers on constrained laptops to build 10GB+ PyTorch/CUDA container images in seconds.
- **Real-World Example**: Developer writes Python code on a lightweight Windows laptop and runs `az acr build`. Azure cloud servers install CUDA, build the image, and store it in ACR.

### Feature 4: Webhooks & Automated CI/CD Deployment Triggers
- **Functionality**: Sends HTTP POST notifications to downstream services whenever new container tags are pushed.
- **Importance for AI Engineers**: Enables continuous deployment (CI/CD). Pushing a new image tag automatically updates live container apps.
- **Real-World Example**: Retrained AI model image `ai-agent:v2.1` is pushed to ACR. Webhook fires to ACA, deploying a new revision with zero user downtime.

### Feature 5: Security Scanning & Vulnerability Management (Microsoft Defender)
- **Functionality**: Integrates with Microsoft Defender for Containers to automatically scan container layers for CVE vulnerabilities.
- **Importance for AI Engineers**: Prevents vulnerable Linux OS packages or outdated Python libraries from reaching production.
- **Real-World Example**: Defender scans a PyTorch container image, flagging an outdated `openssl` package, allowing engineers to patch it before production deployment.

---

## ⚖️ 3. Pros, Advantages & Cons

### ✅ Pros & Advantages:
- **Private & Secure**: Completely enclosed within your Azure Active Directory tenant.
- **Fast Pull Latency**: Co-located in the same Azure data centers as Azure Container Apps & AKS for fast container cold-starts.
- **Docker-less Cloud Build**: `az acr build` eliminates the need for local Docker engines.
- **Fine-Grained Access Control**: Scoped Repository Tokens allow granting access to specific images.

### ❌ Cons & Limitations:
- **Storage Cost Beyond Quota**: Basic SKU includes 10 GB storage; additional storage incur standard gigabyte charges.

---

## 🚀 4. End-to-End Execution Guide in Azure

### Step 1: Create Container Registry & Fetch Credentials (Azure CLI)
```bash
# 1. Create Private Container Registry
az acr create \
  --resource-group rg-explore-ai \
  --name acrexploreai65064 \
  --sku Basic \
  --admin-enabled true

# 2. View Registry Details & Login Server
az acr show --name acrexploreai65064 -o table
```

### Step 2: Create Repository Token & Webhook
```bash
# 1. Create Webhook for push events
az acr webhook create \
  --registry acrexploreai65064 \
  --name aideploywebhook \
  --actions push \
  --uri "https://example.com/api/webhook"

# 2. Create Scoped Token for specific repository
az acr scope-map create \
  --registry acrexploreai65064 \
  --name aiworkerscopemap \
  --repository ai-microservice content/read content/write

az acr token create \
  --registry acrexploreai65064 \
  --name ai-worker-token \
  --scope-map aiworkerscopemap
```

### Step 3: Explore in Azure Portal UI
1. Open [Azure Portal](https://portal.azure.com/) -> **`rg-explore-ai`** -> **`acrexploreai65064`**.
2. Click **Repositories** to view pushed images, layer tags, and SHA digests.
3. Click **Tokens** to view fine-grained repository access tokens.
4. Click **Webhooks** to view active deployment triggers.
