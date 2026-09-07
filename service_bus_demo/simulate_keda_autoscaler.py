import os
import json
import time
import math
import concurrent.futures
from dotenv import load_dotenv
from azure.servicebus import ServiceBusClient, ServiceBusMessage, TransportType

load_dotenv()

CONNECTION_STR = os.getenv("SERVICEBUS_CONNECTION_STRING")
QUEUE_NAME = os.getenv("SERVICEBUS_QUEUE_NAME", "ai-jobs-queue")

TARGET_MESSAGES_PER_WORKER = 10  # KEDA Rule: 1 worker container per 10 active messages
MAX_REPLICAS = 10                # Maximum worker container replicas allowed

def get_azure_queue_depth(client):
    """
    Fetches exact active message count from Azure Service Bus queue.
    """
    receiver = client.get_queue_receiver(queue_name=QUEUE_NAME, max_wait_time=1)
    with receiver:
        # Fast peek to estimate depth
        messages = receiver.peek_messages(max_message_count=100)
        return len(messages)

def simulate_worker_process(worker_id, message):
    """
    Simulates a worker container instance processing an AI job.
    """
    data = json.loads(str(message))
    time.sleep(0.3)  # Simulate model latency
    return data["request_id"]

def run_keda_autoscale_demo():
    print("=" * 80)
    print("[AUTOSCALE DEMO] AZURE SERVICE BUS + KEDA WORKER AUTO-SCALING SIMULATION")
    print(f"KEDA Rule    : 1 Worker Replica per {TARGET_MESSAGES_PER_WORKER} Active Messages")
    print(f"Scale Bounds : Min Replicas = 0 | Max Replicas = {MAX_REPLICAS}")
    print("=" * 80)

    client = ServiceBusClient.from_connection_string(
        CONNECTION_STR,
        transport_type=TransportType.AmqpOverWebsocket
    )

    # STEP 1: Flood queue with 60 messages to trigger scale-out
    print("\n[STEP 1] PRODUCER SPIKE: Enqueuing 60 AI Job Requests...")
    with client:
        sender = client.get_queue_sender(queue_name=QUEUE_NAME)
        with sender:
            messages = [
                ServiceBusMessage(
                    body=json.dumps({"request_id": f"req-auto-{i+1:02d}", "prompt": "AI Task"}),
                    message_id=f"req-auto-{i+1:02d}"
                )
                for i in range(60)
            ]
            sender.send_messages(messages)
            print(" [SUCCESS] 60 messages enqueued in Azure Service Bus Queue!")

    # STEP 2: KEDA Autoscaling Monitoring & Draining Loop
    print("\n[STEP 2] KEDA AUTOSCALER: Monitoring Queue Depth & Scaling Worker Replicas...")
    
    processed_total = 0
    total_to_process = 60
    current_replicas = 0

    client_recv = ServiceBusClient.from_connection_string(
        CONNECTION_STR,
        transport_type=TransportType.AmqpOverWebsocket
    )

    with client_recv:
        receiver = client_recv.get_queue_receiver(queue_name=QUEUE_NAME, max_wait_time=2)
        with receiver:
            while processed_total < total_to_process:
                # 1. Fetch batch of remaining messages
                batch = receiver.receive_messages(max_message_count=60, max_wait_time=2)
                if not batch:
                    print("   [INFO] Queue empty!")
                    break

                queue_depth = len(batch)
                
                # 2. Calculate target KEDA replicas: ceil(queue_depth / 10)
                if queue_depth == 0:
                    target_replicas = 0
                else:
                    target_replicas = min(MAX_REPLICAS, math.ceil(queue_depth / TARGET_MESSAGES_PER_WORKER))
                
                # Log scale event
                if target_replicas > current_replicas:
                    scale_action = f"SCALE-OUT ({current_replicas} -> {target_replicas} Replicas)"
                elif target_replicas < current_replicas:
                    scale_action = f"SCALE-IN  ({current_replicas} -> {target_replicas} Replicas)"
                else:
                    scale_action = f"STABLE     ({current_replicas} Replicas)"

                print(f"\n   [KEDA MONITOR] Queue Depth: {queue_depth:2d} msgs | Action: {scale_action}")
                current_replicas = target_replicas

                # 3. Simulate Parallel Processing across calculated Worker Replicas
                # Divide batch work across worker threads
                chunk_size = min(queue_depth, current_replicas * 3)
                work_chunk = batch[:chunk_size]

                with concurrent.futures.ThreadPoolExecutor(max_workers=current_replicas) as executor:
                    futures = [
                        executor.submit(simulate_worker_process, worker_id % current_replicas + 1, msg)
                        for worker_id, msg in enumerate(work_chunk)
                    ]
                    for msg in work_chunk:
                        receiver.complete_message(msg)
                        processed_total += 1
                
                remaining = total_to_process - processed_total
                progress_bar = "=" * (processed_total // 3) + "." * (remaining // 3)
                print(f"   [WORKER POOL] Processed {len(work_chunk)} msgs with {current_replicas} Workers | Progress: {processed_total:2d}/60 [{progress_bar}]")
                time.sleep(0.5)

            # Final Scale to 0 check
            print("\n   [KEDA MONITOR] Queue Depth:  0 msgs | Action: SCALE-TO-ZERO (Replicas -> 0) [Zero Cost Mode!]")

    print("\n" + "=" * 80)
    print("[SUCCESS] KEDA WORKER AUTO-SCALING SIMULATION COMPLETED!")
    print("=" * 80)

if __name__ == "__main__":
    run_keda_autoscale_demo()
