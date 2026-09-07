# ⚡ Azure Functions (Serverless FaaS): Master Notes for AI Engineers

---

## 📖 1. What is Azure Functions?
**Azure Functions** is an event-driven, serverless compute service (Function-as-a-Service / FaaS) that automatically runs code in response to system events without requiring server infrastructure provisioning or management.

---

## ⚡ 2. Core Features & Functionalities

### Feature 1: Event-Driven Triggers
- **Functionality**: Automatically invokes function code on system events (`BlobTrigger`, `ServiceBusTrigger`, `CosmosDBTrigger`, `TimerTrigger`).
- **Importance for AI Engineers**: Eliminates polling loops. AI data pipelines execute instantly when files or messages arrive.
- **Real-World Example**: A user uploads a 50MB PDF into Azure Blob Storage. A `BlobTrigger` Function fires instantly, extracting text and generating vector embeddings.

### Feature 2: Declarative Input/Output Bindings
- **Functionality**: Connects functions to Azure Cosmos DB, Blob Storage, or Service Bus without writing boilerplate SDK connection code.
- **Importance for AI Engineers**: Reduces 50+ lines of authentication and SDK boilerplate to simple function signature parameters.
- **Real-World Example**: Function receives a prompt via HTTP, calls Azure OpenAI, and automatically saves output to Cosmos DB using an output binding `[CosmosDB]`.

### Feature 3: Premium Elastic Scale (Zero Cold-Start)
- **Functionality**: Keeps pre-warmed worker instances ready while supporting automatic scale-out to hundreds of instances.
- **Importance for AI Engineers**: Eliminates cold-start latency for low-latency AI applications like voice translation or real-time chatbots.
- **Real-World Example**: A medical AI assistant requires sub-second response times. Premium Functions eliminate cold starts, responding in <200ms 24/7.

### Feature 4: Custom Docker Containers
- **Functionality**: Packages functions inside custom Docker containers with pre-installed Linux C++ packages and ML libraries.
- **Importance for AI Engineers**: Overcomes default runtime package/memory limits for heavy AI packages (`OpenCV`, `PyTorch`, `ffmpeg`).
- **Real-World Example**: A video AI processing function requires `ffmpeg` and `OpenCV`. Packaging it in a custom Docker container allows executing video AI serverlessly.

---

## ⚖️ 3. Pros, Advantages & Cons

### ✅ Pros & Advantages:
- **Zero Boilerplate Code**: Declarative bindings handle data connections automatically.
- **Pay-Per-Execution**: Consumption Plan charges strictly per millisecond of execution time.
- **Built-in Event Triggers**: Seamless native triggers for Azure Storage, Event Grid, and Service Bus.
- **Flexible Languages**: Supports Python, C#, JavaScript, TypeScript, Java, and Custom Handlers.

### ❌ Cons & Limitations:
- **Execution Time Limits**: Consumption Plan caps execution time at 10 minutes (Premium Plan supports unlimited execution).
- **Cold Start on Consumption Plan**: Idle Python functions on Consumption Plan incur 3-10 second cold-start delays.

---

## 🚀 4. End-to-End Execution Guide in Azure

### Step 1: Create Storage Account & Function App (Azure CLI)
```bash
# 1. Create Storage Account (Required for Functions metadata)
az storage account create \
  --name stfunctionsai98 \
  --resource-group rg-explore-ai \
  --location eastus \
  --sku Standard_LRS

# 2. Create Python Function App
az functionapp create \
  --name fn-ai-pipeline-app \
  --resource-group rg-explore-ai \
  --storage-account stfunctionsai98 \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4
```

### Step 2: Explore in Azure Portal
1. Open [Azure Portal](https://portal.azure.com/) -> **Resource groups** -> **`rg-explore-ai`** -> **`fn-ai-pipeline-app`**.
2. Click **Functions** in the left menu to view deployed functions, trigger types, and execution logs.
3. Click **Integration** to visually view input and output binding flowcharts.
