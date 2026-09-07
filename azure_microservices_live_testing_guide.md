# Hands-On Azure Microservices Live Testing & Feature Exploration Guide

This document provides a complete hands-on interactive laboratory for testing all 5 core **Azure Microservices** provisioned in your `rg-explore-ai` environment.

---

## Interactive Laboratory Index

- [Lab 1: Azure Container Apps (ACA) — `cae-explore-ai`](#lab-1-azure-container-apps-aca--cae-explore-ai)
- [Lab 2: Azure Service Bus — `sb-explore-ai` (`ai-jobs-queue`)](#lab-2-azure-service-bus--sb-explore-ai-ai-jobs-queue)
- [Lab 3: Azure Container Registry (ACR) — `acrexploreai65064`](#lab-3-azure-container-registry-acr--acrexploreai65064)
- [Lab 4: Azure AI Services — `aiservice-explore-ai`](#lab-4-azure-ai-services--aiservice-explore-ai)
- [Lab 5: Azure Storage & Event Triggers — `stexploreai65064`](#lab-5-azure-storage--event-triggers--stexploreai65064)

---

## Lab 1: Azure Container Apps (ACA) — `cae-explore-ai`

### Goal
Test live HTTP ingress, view provisioned container apps, and inspect active replicas.

#### Step 1: List All Container Apps in Environment
```bash
az containerapp list \
  --resource-group rg-explore-ai \
  --output table
```

#### Step 2: Test Active Container App Endpoint (`aca-ai-agent`)
```powershell
Invoke-RestMethod -Uri "https://aca-ai-agent.yellowwater-c3bd8780.eastus.azurecontainerapps.io/" -Method Get
```

#### Step 3: Inspect Active Container Replicas
```bash
az containerapp replica list \
  --name aca-ai-agent \
  --resource-group rg-explore-ai \
  --output table
```

---

## Lab 2: Azure Service Bus — `sb-explore-ai` (`ai-jobs-queue`)

### Goal
Inspect Service Bus queues (`ai-jobs-queue` & `ai-results-queue`), send test messages, and monitor queue depth.

#### Step 1: List Service Bus Queues & Message Counts
```bash
az servicebus queue list \
  --namespace-name sb-explore-ai \
  --resource-group rg-explore-ai \
  --query "[].{Name:name, Messages:countDetails.activeMessageCount, DeadLetterMessages:countDetails.deadLetterMessageCount, Status:status}" \
  --output table
```

#### Step 2: Send a Test Job Message to `ai-jobs-queue`
```powershell
# Get connection string for sb-explore-ai
$connStr = (az servicebus namespace authorization-rule keys list `
  --namespace-name sb-explore-ai `
  --resource-group rg-explore-ai `
  --name RootManageSharedAccessKey `
  --query primaryConnectionString -o tsv)

Write-Host "Service Bus Connection String retrieved successfully!"
```

#### Step 3: Send Test Message using Azure CLI
```bash
az servicebus queue authorization-rule keys list \
  --namespace-name sb-explore-ai \
  --resource-group rg-explore-ai \
  --queue-name ai-jobs-queue \
  --name RootManageSharedAccessKey
```

---

## Lab 3: Azure Container Registry (ACR) — `acrexploreai65064`

### Goal
Inspect private container registry properties, list repositories, and verify login credentials.

#### Step 1: Query ACR Details & Login Server
```bash
az acr show \
  --name acrexploreai65064 \
  --resource-group rg-explore-ai \
  --query "{Name:name, LoginServer:loginServer, AdminEnabled:adminUserEnabled, Location:location}" \
  --output json
```

#### Step 2: List Repositories in ACR
```bash
az acr repository list \
  --name acrexploreai65064 \
  --output table
```

#### Step 3: Get ACR Credentials (Admin Username & Password)
```bash
az acr credential show \
  --name acrexploreai65064 \
  --output table
```

---

## Lab 4: Azure AI Services — `aiservice-explore-ai`

### Goal
Query AI Services endpoints, retrieve access keys, and list deployed AI models.

#### Step 1: Show Endpoint & Resource Details
```bash
az cognitiveservices account show \
  --name aiservice-explore-ai \
  --resource-group rg-explore-ai \
  --query "{Name:name, Endpoint:properties.endpoint, SKU:sku.name, Location:location}" \
  --output json
```

#### Step 2: Retrieve AI Services API Keys
```bash
az cognitiveservices account keys list \
  --name aiservice-explore-ai \
  --resource-group rg-explore-ai \
  --output table
```

#### Step 3: List Deployed AI Models (Azure OpenAI / Vision)
```bash
az cognitiveservices account deployment list \
  --name aiservice-explore-ai \
  --resource-group rg-explore-ai \
  --output table
```

---

## Lab 5: Azure Storage & Event Triggers — `stexploreai65064`

### Goal
Inspect Blob Storage containers used for document processing triggers.

#### Step 1: List Storage Account Blob Containers
```bash
az storage container list \
  --account-name stexploreai65064 \
  --auth-mode login \
  --output table
```

#### Step 2: Get Storage Account Connection String
```bash
az storage account show-connection-string \
  --name stexploreai65064 \
  --resource-group rg-explore-ai \
  --output tsv
```

---

## Quick Reference Summary Table

| Microservice | Resource Name | CLI Inspection Command |
| :--- | :--- | :--- |
| **Azure Container Apps** | `cae-explore-ai` | `az containerapp list -g rg-explore-ai -o table` |
| **Azure Service Bus** | `sb-explore-ai` | `az servicebus queue list --namespace-name sb-explore-ai -g rg-explore-ai -o table` |
| **Azure Container Registry** | `acrexploreai65064` | `az acr show --name acrexploreai65064 -g rg-explore-ai` |
| **Azure AI Services** | `aiservice-explore-ai` | `az cognitiveservices account show --name aiservice-explore-ai -g rg-explore-ai` |
| **Azure Storage Account** | `stexploreai65064` | `az storage account show --name stexploreai65064 -g rg-explore-ai` |
