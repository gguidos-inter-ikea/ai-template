import pika
import logging
import json
import threading
import time
from fastapi import HTTPException

logger = logging.getLogger("pika client")

class PikaClient:
    def __init__(self, host):
        self.rabbitmq_host = host
        self.connection = None
        self.channel = None
        self._stop_event = threading.Event()  # Event to signal when to stop consuming
        self._shutdown_flag = threading.Event()
        
        self._connect()

    def _connect(self):
        """Establish a connection and channel to RabbitMQ."""
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.rabbitmq_host))
            self.channel = self.connection.channel()
            logger.info("RabbitMQ connection and channel established successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise HTTPException(status_code=500, detail="Failed to connect to RabbitMQ")

    def declare_queue(self, queue_name):
        """Declare a RabbitMQ queue if not already existing."""
        try:
            self.channel.queue_declare(queue=queue_name, durable=True)
            logger.info(f"Declared queue: {queue_name}")
        except Exception as e:
            logger.error(f"Error declaring queue {queue_name}: {e}")
            raise HTTPException(status_code=500, detail="Failed to declare RabbitMQ queue")

    def basic_publish(self, queue_name, message):
        """Publish a message to a specific RabbitMQ queue."""
        try:
            # Reconnect if connection or channel is closed
            if not self.connection or self.connection.is_closed:
                logger.info("RabbitMQ connection is closed. Reconnecting...")
                self._connect()

            # Declare the queue if it doesn't exist
            self.declare_queue(queue_name)

            # Convert message to a JSON string if it's a dictionary
            if isinstance(message, dict):
                message = json.dumps(message)

            # Publish the message
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=message,
                properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
            )
            logger.info(f"Published message to queue '{queue_name}'")
        except pika.exceptions.ChannelClosedByBroker as e:
            logger.error(f"Channel closed by broker during publish: {e}")
            raise HTTPException(status_code=500, detail=f"Channel closed: {e}")
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"Connection error while communicating with RabbitMQ: {e}")
            raise HTTPException(status_code=500, detail=f"Connection error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while publishing to RabbitMQ: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to publish message to RabbitMQ: {e}")

    def consume_messages(self, queue_name, on_message_callback, auto_ack=False):
        """Consume messages from a specific RabbitMQ queue in a non-blocking manner."""
        if self._shutdown_flag.is_set():
            logger.warning(f"Cannot start consuming messages from queue '{queue_name}' during shutdown.")
            return

        while not self._stop_event.is_set() and not self._shutdown_flag.is_set():
            try:
                # Ensure connection is open before consuming
                if not self.connection or self.connection.is_closed:
                    if self._shutdown_flag.is_set():
                        logger.info("Shutdown in progress. Skipping RabbitMQ connection.")
                        return
                    logger.info("RabbitMQ connection is closed. Reconnecting...")
                    self._connect()

                # Declare the queue to ensure it exists
                self.declare_queue(queue_name)

                # Set QoS to control message flow (one message at a time)
                self.channel.basic_qos(prefetch_count=1)

                # Define the on_message callback and store the consumer tag
                self.consumer_tag = self.channel.basic_consume(
                    queue=queue_name,
                    on_message_callback=on_message_callback,
                    auto_ack=auto_ack
                )
                logger.info(f"Started consuming messages from queue '{queue_name}' with consumer tag '{self.consumer_tag}'")

                # Non-blocking consumption loop
                while not self._stop_event.is_set() and not self._shutdown_flag.is_set():
                    self.connection.process_data_events(time_limit=1)

            except pika.exceptions.StreamLostError as e:
                logger.error(f"Stream lost while consuming messages: {e}")
                if not self._shutdown_flag.is_set():
                    logger.info("Attempting to reconnect...")
                    self._connect()
            except Exception as e:
                logger.error(f"Error consuming messages from RabbitMQ queue '{queue_name}': {e}")
                if not self._shutdown_flag.is_set():
                    raise HTTPException(status_code=500, detail="Failed to consume messages from RabbitMQ queue")



    def stop_consuming(self):
        """Signal the consumer to stop and close the connection."""
        self._stop_event.set()
        try:
            if self.channel and self.channel.is_open:
                # Cancel all consumers
                logger.info("Canceling all consumers...")
                try:
                    if hasattr(self, 'consumer_tag') and self.consumer_tag:
                        self.channel.basic_cancel(consumer_tag=self.consumer_tag)
                    else:
                        logger.warning("No valid consumer tag found to cancel.")
                except pika.exceptions.ChannelClosedByBroker:
                    logger.warning("Consumer already canceled or unknown to the broker.")
                time.sleep(0.5)  # Allow pending operations to complete
                self.channel.close()
                logger.info("RabbitMQ channel closed")
        except Exception as e:
            logger.error(f"Error while closing RabbitMQ channel: {e}")
        try:
            if self.connection and self.connection.is_open:
                time.sleep(0.5)  # Allow pending operations to complete
                self.connection.close()
                logger.info("RabbitMQ connection closed")
        except Exception as e:
            logger.error(f"Error while closing RabbitMQ connection: {e}")

    def close_connection(self):
        """Close RabbitMQ connection."""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("Closed RabbitMQ connection")
        except Exception as e:
            logger.error(f"Error while closing RabbitMQ connection: {e}")

    def stop(self):
        """Stop the Pika client."""
        self._shutdown_flag.set()
        self.stop_consuming()
        self.close_connection()