from src.base.repositories.rabbitmq_repository import RabbitMQRepository
import logging
import json

logger = logging.getLogger(__name__)

class ConsumeQueue:
    def __init__(self, repository: RabbitMQRepository):
        """
        Initialize the ConsumeQueue class.

        Args:
            repository (RabbitMQRepository): The RabbitMQ repository for interacting with RabbitMQ.
            error_queue (str): The name of the queue to publish exceptions to.
        """
        self.repository = repository

    def execute(self, queue_name: str, on_message_callback):
        """
        Start consuming messages from the specified RabbitMQ queue.

        Args:
            queue_name (str): The name of the RabbitMQ queue to consume from.
            on_message_callback (function): The callback function to process messages.
        """
        logger.info(f"Starting to consume messages from queue: {queue_name}")
        return self.repository.consume_queue(queue_name, on_message_callback)

    def publish_exception(self, exception: Exception, queue_name: str, original_message: str):
        """
        Publish an exception to the error queue.

        Args:
            exception (Exception): The exception that occurred.
            queue_name (str): The name of the queue where the error occurred.
            original_message (str): The original message that caused the exception.
        """
        error_message = {
            "error": str(exception),
            "queue": queue_name,
            "original_message": original_message,
        }
        try:
            self.repository.publish_message(self.error_queue, json.dumps(error_message))
            logger.info(f"Published exception to error queue: {error_message}")
        except Exception as e:
            logger.error(f"Failed to publish exception to error queue: {e}")

    def start_rabbitmq_consumer(self, queue_name: str, process_message_callback):
        """
        Start consuming messages from the specified RabbitMQ queue.

        Args:
            queue_name (str): The name of the RabbitMQ queue to consume from.
            process_message_callback (function): A user-defined callback to process messages.
        """
        def on_message(ch, method, properties, body):
            """
            Callback function to process messages from the RabbitMQ queue.

            Args:
                ch: The channel object.
                method: The delivery method.
                properties: The message properties.
                body: The message body.
            """
            try:
                # Decode the message body
                message = body.decode("utf-8")
                logger.info(f"Received message from queue '{queue_name}': {message}")

                # Call the user-defined processing function
                process_message_callback(message)

                # Acknowledge the message
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.error(f"Failed to process message from queue '{queue_name}': {e}")
                # Publish the exception to the error queue
                self.publish_exception(e, queue_name, body.decode("utf-8"))
                # Reject the message without requeueing
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        # Start consuming messages from the queue
        self.execute(queue_name, on_message)

    def close_connection(self):
        """
        Close the connection to RabbitMQ.
        """
        self.repository.close_connection()