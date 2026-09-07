# Azure Service Bus: Live Analysis & Hands-On Testing Guide

---

## 📊 Part 1: How to Analyze the Live Output

When you run an asynchronous AI workflow through Azure Service Bus, the terminal output reflects core enterprise messaging features.

### Terminal Log Breakdown & Feature Mapping

```text
--- [STEP 1] PRODUCER: Enqueuing AI Document Processing Jobs ---
  [ENQUEUED] ID=job-rag-9faa06 | File='Annual_Financial_Report_2025.pdf' | Model=text-embedding-3-small | Priority=HIGH
  [ENQUEUED] ID=job-summary-d1365b | File='Executive_Brief.docx' | Model=gpt-4o | Priority=NORMAL
  [ENQUEUED] ID=job-transcription-0d85d8 | File='Earnings_Call_Audio.mp3' | Model=whisper-large-v3 | Priority=HIGH
  [ENQUEUED] ID=job-corrupt-a20ccc | File='Encrypted_Corrupted_File.bin' | Model=text-embedding-3-small | Priority=LOW
 [SUCCESS] Batch of 4 messages successfully delivered to Azure Service Bus Queue!
```
- **Feature Demonstrated**: **Batch Sending & Custom Metadata**.
  - All 4 messages were sent in a single atomic network request.
  - Metadata (`model`, `priority`, `task_type`) is attached to message headers (`application_properties`), allowing downstream workers or Azure Function filters to inspect properties without parsing the body.

---

```text
--- [STEP 2] CONSUMER: Processing Messages using Peek-Lock ---

  [LOCK ACQUIRED] 'job-rag-9faa06' (Delivery Count: 0)
     Payload: File='Annual_Financial_Report_2025.pdf', Task='rag_embeddings'
     [SUCCESS] AI Task 'rag_embeddings' completed for 'Annual_Financial_Report_2025.pdf'.
     [COMPLETED] Message 'job-rag-9faa06' removed from Queue.
```
- **Feature Demonstrated**: **Peek-Lock Mode (`complete_message`)**.
  - `Lock Acquired`: The consumer locks the message so no other auto-scaled worker can process it simultaneously.
  - `Delivery Count: 0`: First time this message is being attempted.
  - `[COMPLETED]`: The message was successfully acknowledged and permanently deleted from Azure Service Bus.

---

```text
  [LOCK ACQUIRED] 'job-corrupt-a20ccc' (Delivery Count: 0)
     Payload: File='Encrypted_Corrupted_File.bin', Task='rag_embeddings'
     [ERROR] Processing Failure: Unreadable format in 'Encrypted_Corrupted_File.bin'.
     [RETRY] Abandoning lock for retry #1...

  [LOCK ACQUIRED] 'job-corrupt-a20ccc' (Delivery Count: 1)
     Payload: File='Encrypted_Corrupted_File.bin', Task='rag_embeddings'
     [ERROR] Processing Failure: Unreadable format in 'Encrypted_Corrupted_File.bin'.
     [DLQ ROUTING] Max Retries Exceeded! Moving message 'job-corrupt-a20ccc' to DEAD-LETTER QUEUE (DLQ)...
     [DLQ MOVED] Message moved to DLQ sub-queue safely.
```
- **Feature Demonstrated**: **Lock Abandonment & Dead-Letter Queue (DLQ) Isolation**.
  - On attempt #0: Processing failed. The consumer called `receiver.abandon_message(msg)`. This instantly releases the lock back to Azure Service Bus.
  - On attempt #1: Delivery count reached `1`. `max_delivery_count` limit triggered. The consumer called `receiver.dead_letter_message(...)`.
  - The corrupted message is safely moved to the **Dead-Letter Queue (DLQ)** sub-queue with a custom error reason (`UnreadableDocumentFormat`), ensuring that healthy queue processing is never blocked!

---

## 🔍 Part 2: How to View Features & Results in Azure

### Method A: Via Azure Portal (Visual UI Inspection)

1. Open [Azure Portal](https://portal.azure.com/).
2. Navigate to **Resource groups** -> **`rg-explore-ai`** -> **`sb-explore-ai`** (Service Bus Namespace).
3. **Inspect Main Queue**:
   - Go to **Entities** -> **Queues** -> **`ai-jobs-queue`**.
   - View the Overview metrics panel:
     - `Active message count`: Should be `0` (All valid messages completed!).
     - `Dead-letter message count`: Should be `2` (Corrupted messages stored safely!).
4. **Inspect Dead-Letter Queue (DLQ) Contents**:
   - Click **Service Bus Explorer** in the left menu.
   - At the top, change **Queue type** from *Main queue* to **Dead-letter queue**.
   - Select **Peek from start** -> click **Peek**.
   - Click on the dead-lettered message (`job-corrupt-a20ccc`) to inspect:
     - **DeadLetterReason**: `UnreadableDocumentFormat`
     - **DeadLetterErrorDescription**: `File header corrupted or password protected.`
     - **Message Body**: Full JSON payload preserved for developer debugging.
5. **Inspect Pub/Sub Topic & Subscription**:
   - Go to **Entities** -> **Topics** -> **`ai-events-topic`** -> **Subscriptions** -> **`analytics-sub`**.
   - Click **Service Bus Explorer** -> **Peek from start**.
   - You will see active event messages published by `topic_pubsub.py` waiting for subscribers!

---

### Method B: Via Azure CLI (Command Line Verification)

Run these commands in your PowerShell / Terminal:

#### 1. Check Queue Metrics (Active & Dead-Letter Counts)
```bash
az servicebus queue show \
  --resource-group rg-explore-ai \
  --namespace-name sb-explore-ai \
  --name ai-jobs-queue \
  --query "countDetails" -o json
```
*Expected Output:*
```json
{
  "activeMessageCount": 0,
  "deadLetterMessageCount": 2,
  "scheduledMessageCount": 0
}
```

#### 2. Check Topic Subscription Metrics
```bash
az servicebus topic subscription show \
  --resource-group rg-explore-ai \
  --namespace-name sb-explore-ai \
  --topic-name ai-events-topic \
  --name analytics-sub \
  --query "countDetails" -o json
```

---

## 🛠️ Part 3: Steps to Run an Example Yourself

### Option 1: Run the Interactive Python Pipeline

1. Open your Terminal / PowerShell.
2. Change directory to the demo folder:
   ```bash
   cd c:\Users\2869026\Desktop\up\service_bus_demo
   ```
3. Run the live pipeline script:
   ```bash
   python live_ai_pipeline.py
   ```
4. Observe the terminal as it connects to Azure Service Bus via WebSockets, enqueues 4 jobs, processes valid jobs, retries the corrupted job, and routes it to the Dead-Letter Queue!

---

### Option 2: Send & Receive Messages Custom Scripts

You can also run producer and consumer in separate terminal windows to simulate real distributed microservices!

- **Terminal 1 (Producer)**:
  ```bash
  cd c:\Users\2869026\Desktop\up\service_bus_demo
  python producer.py
  ```
- **Terminal 2 (Consumer)**:
  ```bash
  cd c:\Users\2869026\Desktop\up\service_bus_demo
  python consumer.py
  ```
- **Terminal 3 (Topic Publisher)**:
  ```bash
  cd c:\Users\2869026\Desktop\up\service_bus_demo
  python topic_pubsub.py
  ```

---

### Option 3: Send a Custom Test Message from Azure Portal

1. Go to **Azure Portal** -> **Resource groups** -> **`rg-explore-ai`** -> **`sb-explore-ai`** -> **Queues** -> **`ai-jobs-queue`**.
2. Click **Service Bus Explorer** -> **Send messages**.
3. Set **Content type** to `application/json`.
4. Paste a custom AI job payload:
   ```json
   {
     "job_id": "my-manual-job-001",
     "document_name": "My_Custom_Prompt.txt",
     "task": "llm_summary",
     "model": "gpt-4o",
     "corrupt": false
   }
   ```
5. Click **Send**.
6. In your terminal, run `python consumer.py` to watch your local Python consumer pick up and process the message you sent from the Azure Portal!
