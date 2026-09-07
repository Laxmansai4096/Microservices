import os
import json
import time
import uuid
from dotenv import load_dotenv
from azure.servicebus import ServiceBusClient, ServiceBusMessage, TransportType

load_dotenv()

CONNECTION_STR = os.getenv("SERVICEBUS_CONNECTION_STRING")
QUEUE_NAME = os.getenv("SERVICEBUS_QUEUE_NAME", "ai-jobs-queue")

def run_live_pipeline_demo():
    print("=" * 70)
    print("[DEMO] AZURE SERVICE BUS LIVE AI WORKFLOW DEMO")
    print(f"Target Resource Group : rg-explore-ai")
    print(f"Target Namespace      : sb-explore-ai")
    print(f"Target Queue          : {QUEUE_NAME}")
    print("=" * 70)
    
    client = ServiceBusClient.from_connection_string(
        CONNECTION_STR,
        transport_type=TransportType.AmqpOverWebsocket
    )

    # -------------------------------------------------------------
    # STEP 1: PRODUCER - Enqueue batch of 4 AI Document Jobs
    # -------------------------------------------------------------
    print("\n--- [STEP 1] PRODUCER: Enqueuing AI Document Processing Jobs ---")
    jobs = [
        {
            "job_id": f"job-rag-{uuid.uuid4().hex[:6]}",
            "document_name": "Annual_Financial_Report_2025.pdf",
            "task": "rag_embeddings",
            "model": "text-embedding-3-small",
            "priority": "HIGH",
            "corrupt": False
        },
        {
            "job_id": f"job-summary-{uuid.uuid4().hex[:6]}",
            "document_name": "Executive_Brief.docx",
            "task": "llm_summary",
            "model": "gpt-4o",
            "priority": "NORMAL",
            "corrupt": False
        },
        {
            "job_id": f"job-transcription-{uuid.uuid4().hex[:6]}",
            "document_name": "Earnings_Call_Audio.mp3",
            "task": "whisper_transcription",
            "model": "whisper-large-v3",
            "priority": "HIGH",
            "corrupt": False
        },
        {
            "job_id": f"job-corrupt-{uuid.uuid4().hex[:6]}",
            "document_name": "Encrypted_Corrupted_File.bin",
            "task": "rag_embeddings",
            "model": "text-embedding-3-small",
            "priority": "LOW",
            "corrupt": True  # Will test DLQ auto-deadlettering
        }
    ]

    with client:
        sender = client.get_queue_sender(queue_name=QUEUE_NAME)
        with sender:
            sb_messages = []
            for job in jobs:
                msg = ServiceBusMessage(
                    body=json.dumps(job),
                    message_id=job["job_id"],
                    content_type="application/json",
                    application_properties={
                        "model": job["model"],
                        "priority": job["priority"],
                        "task_type": job["task"]
                    }
                )
                sb_messages.append(msg)
                print(f"  [ENQUEUED] ID={job['job_id']} | File='{job['document_name']}' | Model={job['model']} | Priority={job['priority']}")
            
            sender.send_messages(sb_messages)
            print(f" [SUCCESS] Batch of {len(sb_messages)} messages successfully delivered to Azure Service Bus Queue!\n")

        # -------------------------------------------------------------
        # STEP 2: CONSUMER - Peek-Lock Processing & Error Isolation
        # -------------------------------------------------------------
        print("--- [STEP 2] CONSUMER: Processing Messages using Peek-Lock ---")
        receiver = client.get_queue_receiver(queue_name=QUEUE_NAME, max_wait_time=5)
        with receiver:
            for msg in receiver:
                data = json.loads(str(msg))
                job_id = data["job_id"]
                doc_name = data["document_name"]
                is_corrupt = data.get("corrupt", False)
                
                print(f"\n  [LOCK ACQUIRED] '{job_id}' (Delivery Count: {msg.delivery_count})")
                print(f"     Payload: File='{doc_name}', Task='{data['task']}'")

                if is_corrupt:
                    print(f"     [ERROR] Processing Failure: Unreadable format in '{doc_name}'.")
                    if msg.delivery_count >= 1:
                        print(f"     [DLQ ROUTING] Max Retries Exceeded! Moving message '{job_id}' to DEAD-LETTER QUEUE (DLQ)...")
                        receiver.dead_letter_message(
                            msg,
                            reason="UnreadableDocumentFormat",
                            error_description="File header corrupted or password protected."
                        )
                        print(f"     [DLQ MOVED] Message moved to DLQ sub-queue safely.")
                    else:
                        print(f"     [RETRY] Abandoning lock for retry #1...")
                        receiver.abandon_message(msg)
                else:
                    time.sleep(1)  # Simulate AI model latency
                    print(f"     [SUCCESS] AI Task '{data['task']}' completed for '{doc_name}'.")
                    receiver.complete_message(msg)
                    print(f"     [COMPLETED] Message '{job_id}' removed from Queue.")

    print("\n" + "=" * 70)
    print("[SUCCESS] LIVE PIPELINE DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_live_pipeline_demo()
