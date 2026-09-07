# 🔎 How to View and Implement AI Agents in Azure

---

## 🧭 Overview: How Agents Exist in Azure

In the Azure cloud ecosystem, AI Agents are not just standalone scripts; they are implemented using **two primary production architectures**:

1. **Architecture A: Containerized Autonomous Agent Microservices (Azure Container Apps - ACA)**
   * Built using frameworks like **Microsoft AutoGen**, **Semantic Kernel**, or **LangGraph**.
   * Deployed as a scalable container with REST APIs or asynchronous Service Bus queue consumers.
   * *Status in your Azure Account*: You have an active container app named **`aca-ai-agent`** running in **`rg-explore-ai`**!

2. **Architecture B: Azure AI Agent Service (Azure AI Foundry / Studio)**
   * A fully managed PaaS agent runtime provided by Azure (equivalent to enterprise Assistants API).
   * Azure manages persistent conversation threads, state management, file vector stores, and tool execution loops.

---

## 📍 Method 1: Inspect Your Live Agent in Azure Container Apps

You already have a dedicated AI Agent container app provisioned in your resource group:

### 1. Inspect via Azure CLI
```bash
az containerapp show \
  --name aca-ai-agent \
  --resource-group rg-explore-ai \
  --query "{Name:name, FQDN:properties.configuration.ingress.fqdn, Image:properties.template.containers[0].image, MinReplicas:properties.template.scale.minReplicas, MaxReplicas:properties.template.scale.maxReplicas}" \
  -o json
```

*Live Configuration in your Azure Account:*
* **Name**: `aca-ai-agent`
* **FQDN / URL**: `aca-ai-agent.yellowwater-c3bd8780.eastus.azurecontainerapps.io`
* **Scale Bounds**: Min Replicas: `1`, Max Replicas: `3`
* **Auto-scale Rule**: `http-rule` (Triggers scaling when concurrent requests exceed 1).

### 2. View in Azure Portal
1. Open [Azure Portal](https://portal.azure.com/).
2. Navigate to **Resource groups** -> **`rg-explore-ai`** -> **`aca-ai-agent`**.
3. **Log Stream (Live Agent Thoughts)**:
   * In the left menu under *Monitoring*, click **Log stream**.
   * As user queries arrive, you can watch the agent's live console output: reasoning steps, tool invocations, and synthesized responses.
4. **Scale & Replicas**:
   * Click **Scale** to view the active replica count and scale rules.
   * Click **Console** to open an interactive terminal directly inside the running agent container.

---

## 📍 Method 2: Azure AI Agent Service (Azure AI Foundry Portal)

For managed serverless agents:

1. Open the [Azure AI Foundry Portal](https://ai.azure.com/).
2. Select your Azure subscription and navigate to your AI Project or Hub (associated with `aiservice-explore-ai`).
3. Click **Agents** (or **Assistants**) in the left sidebar:
   * **Agent Playground**: Interactive UI to chat with the agent, test tool calls, and inspect thread messages.
   * **Tools Tab**: Attach tools with a single click:
     * *Code Interpreter*: Enables dynamic Python data analysis.
     * *Azure AI Search*: Connects your vector index as a RAG tool.
     * *OpenAPI / Custom Functions*: Connects Azure Functions as REST tools.
   * **Thread State**: View message histories and run step statuses (`in_progress`, `requires_action`, `completed`).

---

## 🧪 Method 3: Live End-to-End Multi-Agent Execution Flow

In your workspace, you can run the full multi-tier agent flow that demonstrates how agents interact with tools, sandboxes, and human approvers:

```bash
cd c:\Users\2869026\Desktop\up
python azure_ai_agents/multi_agent_pipeline_demo.py
```

### What You See in the Trace:
1. **Financial Analysis Agent**:
   * Calls SQL Database Tool (`tool_database_lookup`).
   * Invokes Python Sandbox Tool (`tool_dynamic_code_interpreter`) to compute exact Debt-to-Income ratio (28.00%).
2. **Compliance & Policy Agent**:
   * Calls Azure AI Search Tool (`tool_regulatory_rag_search`) to retrieve lending policies.
   * Verifies DTI and credit score thresholds.
3. **Supervisor Orchestrator & Human Gate**:
   * Detects high-value transaction ($250,000 > $100,000 threshold).
   * Suspends workflow, emits an event, and awaits human VP sign-off before loan fund disbursement!
