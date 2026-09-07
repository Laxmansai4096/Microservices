import os
import json
import uuid
import time
from dotenv import load_dotenv
from azure.servicebus import ServiceBusClient, ServiceBusMessage, TransportType

load_dotenv()

CONNECTION_STR = os.getenv("SERVICEBUS_CONNECTION_STRING")
QUEUE_NAME = os.getenv("SERVICEBUS_QUEUE_NAME", "ai-jobs-queue")

def send_ai_jobs():
    print(f"Connecting to Azure Service Bus Queue: '{QUEUE_NAME}' via WebSockets (Port 443)...")
    client = ServiceBusClient.from_connection_string(
        CONNECTION_STR,
        transport_type=TransportType.AmqpOverWebsocket
    )
    
    with client:
        sender = client.get_queue_sender(queue_name=QUEUE_NAME)
        with sender:
            # Batch of AI workload requests
            jobs = [
                {
                    "job_id": str(uuid.uuid4()),
                    "task": "summarize_document",
                    "payload": {"text": "Azure Service Bus enables asynchronous microservices communication..."},
                    "model": "gpt-4o",
                    "should_fail": False
                },
                {
                    "job_id": str(uuid.uuid4()),
                    "task": "generate_embeddings",
                    "payload": {"chunks": ["Chunk 1 text...", "Chunk 2 text..."]},
                    "model": "text-embedding-3-small",
                    "should_fail": False
                },
                {
                    "job_id": str(uuid.uuid4()),
                    "task": "poison_job_test",
                    "payload": {"invalid_data": None},
                    "model": "gpt-4o",
                    "should_fail": True  # Will test Dead-Letter Queue handling
                }
            ]
            
            messages = []
            for job in jobs:
                body_json = json.dumps(job)
                msg = ServiceBusMessage(
                    body=body_json,
                    message_id=job["job_id"],
                    content_type="application/json",
                    application_properties={
                        "model": job["model"],
                        "task_type": job["task"],
                        "environment": "production"
                    }
                )
                messages.append(msg)
                print(f"[Producer] Prepared job {job['job_id']} (Task: {job['task']}, Model: {job['model']})")

            # Send messages as a batch
            sender.send_messages(messages)
            print(f"Successfully sent {len(messages)} AI jobs to queue '{QUEUE_NAME}'.")

if __name__ == "__main__":
    send_ai_jobs()
