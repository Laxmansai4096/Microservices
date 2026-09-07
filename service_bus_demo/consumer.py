import os
import json
import time
from dotenv import load_dotenv
from azure.servicebus import ServiceBusClient, TransportType

load_dotenv()

CONNECTION_STR = os.getenv("SERVICEBUS_CONNECTION_STRING")
QUEUE_NAME = os.getenv("SERVICEBUS_QUEUE_NAME", "ai-jobs-queue")

def process_ai_job(message):
    body_str = str(message)
    data = json.loads(body_str)
    
    task = data.get("task")
    job_id = data.get("job_id")
    should_fail = data.get("should_fail", False)
    
    print(f"\n[Consumer] Processing AI Job '{job_id}'...")
    print(f"            Task Type: {task}")
    print(f"            App Properties: {message.application_properties}")
    print(f"            Delivery Count: {message.delivery_count}")

    if should_fail:
        raise ValueError(f"Poison message detected! Task '{task}' contains corrupted payload.")
    
    # Simulate LLM API Call latency
    time.sleep(1.5)
    print(f" SUCCESS: Processed AI job '{job_id}' using model '{data.get('model')}'.")

def receive_ai_jobs():
    print(f"Starting Consumer for Azure Service Bus Queue: '{QUEUE_NAME}' via WebSockets (Port 443)...")
    client = ServiceBusClient.from_connection_string(
        CONNECTION_STR,
        transport_type=TransportType.AmqpOverWebsocket
    )
    
    with client:
        receiver = client.get_queue_receiver(queue_name=QUEUE_NAME, max_wait_time=5)
        with receiver:
            for msg in receiver:
                try:
                    process_ai_job(msg)
                    # Complete the message to remove it from the queue
                    receiver.complete_message(msg)
                    print(f" [Peek-Lock] Message '{msg.message_id}' COMPLETED and removed from queue.")
                except Exception as e:
                    print(f" ERROR processing message '{msg.message_id}': {e}")
                    
                    if msg.delivery_count >= 2:
                        # Move directly to Dead-Letter Queue (DLQ) if max retries exceeded
                        print(f" [DLQ] Moving message '{msg.message_id}' to Dead-Letter Queue...")
                        receiver.dead_letter_message(
                            msg,
                            reason="CorruptedPayloadOrMaxRetries",
                            error_description=str(e)
                        )
                    else:
                        # Abandon lock so message can be retried by worker
                        print(f" [Abandon] Abandoning message lock for retry (Delivery attempt #{msg.delivery_count})...")
                        receiver.abandon_message(msg)

if __name__ == "__main__":
    receive_ai_jobs()
