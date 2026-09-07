import os
import json
import uuid
import time
from dotenv import load_dotenv
from azure.servicebus import ServiceBusClient, ServiceBusMessage, TransportType

load_dotenv()

CONNECTION_STR = os.getenv("SERVICEBUS_CONNECTION_STRING")
TOPIC_NAME = os.getenv("SERVICEBUS_TOPIC_NAME", "ai-events-topic")

def publish_agent_event():
    """
    Publishes an event to a Topic so multiple AI agent subscribers (e.g. Guardrails, RAG, Summarizer)
    can consume it independently.
    """
    print(f"Connecting to Azure Service Bus Topic: '{TOPIC_NAME}' via WebSockets (Port 443)...")
    client = ServiceBusClient.from_connection_string(
        CONNECTION_STR,
        transport_type=TransportType.AmqpOverWebsocket
    )
    
    with client:
        sender = client.get_topic_sender(topic_name=TOPIC_NAME)
        with sender:
            event_id = str(uuid.uuid4())
            payload = {
                "event_id": event_id,
                "user_id": "usr_77812",
                "prompt": "Analyze customer financial report for compliance and generate summary",
                "timestamp": time.time()
            }
            
            message = ServiceBusMessage(
                body=json.dumps(payload),
                message_id=event_id,
                content_type="application/json",
                application_properties={
                    "event_type": "USER_PROMPT_SUBMITTED",
                    "requires_pii_check": True,
                    "target_agent": "multi_agent_pipeline"
                }
            )
            
            sender.send_messages(message)
            print(f"[Topic Publisher] Published event {event_id} with event_type='USER_PROMPT_SUBMITTED'.")

if __name__ == "__main__":
    publish_agent_event()
