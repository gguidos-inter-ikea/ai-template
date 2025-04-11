import json
import logging
from threading import Thread

logger = logging.getLogger(__name__)

def process_message_callback(message: str):
    """
    Callback function to process messages from RabbitMQ.
    
    Args:
        message (str): The message received from RabbitMQ.
    """
    try:
        # Parse the message as JSON
        message_data = json.loads(message)
        
        # Extract and log the event type
        event_type = message_data.get("event_type", "unknown")
        logger.info(f"Received event type: {event_type}")
    except json.JSONDecodeError:
        logger.error(f"Failed to decode message: {message}")
    except Exception as e:
        logger.error(f"Error processing message: {e}")

def start_consumer(consumer, queue_name, callback):
    """
    Start the RabbitMQ consumer in a separate thread.
    
    Args:
        consumer: The RabbitMQ consumer instance.
        queue_name (str): The name of the RabbitMQ queue to consume from.
        callback (function): The callback function to process messages.
    """
    def consumer_thread():
        consumer.start_rabbitmq_consumer(
            queue_name=queue_name,
            process_message_callback=callback
        )
    
    thread = Thread(target=consumer_thread, daemon=True)
    thread.start()
    logger.info("RabbitMQ consumer thread started.")
    return thread