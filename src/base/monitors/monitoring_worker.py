import pika
import json
import logging

logger = logging.getLogger(__name__)

class MonitoringWorker:
    """Worker for processing monitoring events."""

    def __init__(self, rabbitmq_host: str, queue_name: str):
        self.rabbitmq_host = rabbitmq_host
        self.queue_name = queue_name

    def process_message(self, ch, method, properties, body):
        """Process a message from RabbitMQ."""
        try:
            message = json.loads(body)
            event_type = message.get("event_type")
            details = message.get("details")

            if event_type == "error":
                self.handle_error_event(details)
            elif event_type == "security":
                self.handle_security_event(details)
            else:
                logger.warning(f"Unknown event type: {event_type}")

            # Acknowledge the message
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag)

    def handle_error_event(self, details):
        """Handle error events."""
        logger.error(f"Error event: {details}")
        # Add logic to send email alerts or log to an external system

    def handle_security_event(self, details):
        """Handle security events."""
        logger.warning(f"Security event: {details}")
        # Add logic to send security alerts

    def start(self):
        """Start consuming messages."""
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.rabbitmq_host))
        channel = connection.channel()
        channel.queue_declare(queue=self.queue_name, durable=True)

        channel.basic_consume(queue=self.queue_name, on_message_callback=self.process_message)
        logger.info("Monitoring worker started. Waiting for messages...")
        channel.start_consuming()