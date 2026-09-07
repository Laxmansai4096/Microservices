# Azure Container Registry (ACR): Live Working Exploration Walkthrough

---

## 🎯 Live Azure Resources Configured & Explored

We configured and analyzed your live Azure Container Registry inside `rg-explore-ai`:

| Property | Value / Status |
| :--- | :--- |
| **Resource Group** | `rg-explore-ai` |
| **Registry Name** | `acrexploreai65064` |
| **Login Server** | `acrexploreai65064.azurecr.io` |
| **SKU** | `Basic` (10 GB Included Storage) |
| **Admin User** | `Enabled` |
| **Live Webhook Created** | `aideploywebhook` (Status: `enabled`, Action: `push`) |
| **Repository Scope Map Created** | `aiworkerscopemap` (Action: `ai-microservice read/write`) |
| **Repository Token Created** | `ai-worker-token` |

---

## 🛠️ Live Feature Demos Executed in Your Azure Account

### Feature 1: Scope Maps & Repository Tokens (Fine-Grained Security)
Rather than sharing global admin passwords, we created a **Repository Token** (`ai-worker-token`) linked to `aiworkerscopemap`.
- **Functionality**: Limits authentication strictly to the `ai-microservice` repository.
- **Verification via CLI**:
  ```bash
  az acr token list --registry acrexploreai65064 -o table
  ```

### Feature 2: Automated Deployment Webhooks
We created a live **Webhook** `aideploywebhook` on `acrexploreai65064`.
- **Functionality**: Fires an HTTP POST payload whenever an engineer or CI/CD pipeline pushes a new container image tag.
- **Verification via CLI**:
  ```bash
  az acr webhook list --registry acrexploreai65064 -o table
  ```

### Feature 3: Storage Usage & Quota Metrics
We queried the active quota limits for `acrexploreai65064`:
- **Current Storage Used**: `0 Bytes`
- **Max Storage Limit**: `10 GB` (`10,737,418,240 Bytes`)
- **Max Webhooks Allowed**: `2`
- **Max Tokens Allowed**: `100`

---

## 🌐 Step-by-Step Instructions to View These Features in Azure Portal

1. Open [Azure Portal](https://portal.azure.com/).
2. Go to **Resource groups** -> **`rg-explore-ai`** -> **`acrexploreai65064`** (Container registry).

### A. View Tokens & Scope Maps (Security)
- In the left menu under **Settings**, click **Tokens**.
- You will see the token we created: **`ai-worker-token`** connected to **`aiworkerscopemap`**!

### B. View Live Webhooks
- In the left menu under **Services**, click **Webhooks**.
- You will see the webhook we created: **`aideploywebhook`** (Action: `push`, Status: `enabled`).

### C. View Access Keys (Admin Auth)
- In the left menu under **Settings**, click **Access keys**.
- View your registry FQDN `acrexploreai65064.azurecr.io`, Username, and primary password.
