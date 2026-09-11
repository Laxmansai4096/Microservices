# How to View & Create Agents in Azure AI Foundry Portal

We have successfully provisioned your **Azure AI Foundry Hub & Project** inside `rg-explore-ai`!

---

## 🏛️ Your Azure AI Foundry Resources

| Resource Type | Resource Name | Resource Group | Region | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Foundry Hub** | `hub-explore-ai` | `rg-explore-ai` | `eastus` | Enterprise governance, security, and storage container |
| **Foundry Project** | `prj-explore-ai` | `rg-explore-ai` | `eastus` | Workspace for creating and testing AI Agents |
| **Azure OpenAI Service** | `openai-explore-ai` | `rg-explore-ai` | `eastus` | Model hosting & inference engine |
| **Model Deployment** | `gpt-5-mini` | `rg-explore-ai` | `eastus` | State-of-the-art agent model with tools support |

---

## 🌐 How to Access Your Project in Azure AI Foundry

1. Open your browser and navigate directly to:
   👉 **[https://ai.azure.com](https://ai.azure.com)**
2. Sign in with your Azure account (`uma26932@gmail.com`).
3. In the top-left project switcher, select:
   * **Subscription**: `Azure subscription 1`
   * **Resource Group**: `rg-explore-ai`
   * **Project**: `prj-explore-ai`
4. Or use this direct deep link to your project:
   👉 [Open `prj-explore-ai` in Azure AI Foundry](https://ai.azure.com/build/overview?wsid=/subscriptions/6fb67c72-73dc-4767-a210-0ea6b6c99feb/resourcegroups/rg-explore-ai/providers/Microsoft.MachineLearningServices/workspaces/prj-explore-ai)

---

## 🤖 Creating Agents in the Foundry Portal UI

Inside **`prj-explore-ai`**:

1. In the left-hand navigation menu under **Build**, click on **Agents**.
2. Click **+ Create agent** (or **+ New Agent**).
3. Configure your agent:
   * **Name**: `DataAnalystAgent` or `EnterpriseSupervisor`
   * **Instructions / System Prompt**: Define the agent's persona and responsibilities.
   * **Model**: Select `gpt-5-mini` from the connected Azure OpenAI service.
4. Add Capabilities / Tools:
   * **Code Interpreter**: Enable Python execution sandbox for math, data charts, and dynamic transformations.
   * **Knowledge / File Search (RAG)**: Attach documents or vector indexes from Azure AI Search.
   * **Functions / OpenAPI**: Add custom REST API tools (e.g. your Azure SQL or Cosmos DB endpoints).
5. Click **Try in Playground** to chat with your agent in real time on the Foundry portal canvas!

---

## ⚖️ Code-First vs. Foundry UI Agents

| Dimension | Code-First Orchestration (`live_azure_agent_ecosystem.py`) | Foundry UI Agents (`ai.azure.com`) |
| :--- | :--- | :--- |
| **Where it runs** | Python app / Azure Container Apps / Functions | Azure AI Agent Service managed cloud infrastructure |
| **Database Flexibility** | Direct connection to SQL, Cosmos DB, SQLite, MongoDB, Redis | Requires OpenAPI wrappers, Azure AI Search, or Fabric IQ |
| **A2A Multi-Agent** | Custom Supervisor, Swarms, sequential pipelines with full audit code | Agent-to-Agent via Azure Agent Service multi-agent preview |
| **UI Playground** | Console / Web App UI / Streamlit / FastAPI | Built-in Azure AI Foundry Chat Canvas & Tracing UI |
| **Best For** | Complex enterprise microservices & multi-database transactional workflows | Quick prototyping, RAG knowledge bots, and non-developer authoring |
