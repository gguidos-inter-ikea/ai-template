"""
Lifespan context manager for FastAPI application.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from src.base.config.config import settings
from src.base.lifespan.utils import process_message_callback, start_consumer
import logging

logger = logging.getLogger("lifespan")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    
    # Get Redis instance from dependency injection container
    container = app.container
    redis_instance = container.redis.redis_client()

    # Initialize FastAPILimiter with Redis
    await FastAPILimiter.init(redis_instance)
    logger.info("FastAPILimiter initialized with Redis")
    
    # Initialize MongoDB connection
    mongo_client = container.database.mongo_client()

    # Start RabbitMQ consumer
    logger.info("Starting RabbitMQ consumer...")
    consumer = container.messaging.consumer()
    consumer_thread = start_consumer(
        consumer=consumer,
        queue_name=settings.messaging.rabbitmq_monitoring_queue,
        callback=process_message_callback
    )

    try:
        # Test Redis connection
        await redis_instance.ping()
        logger.info("Rate limiter initialized with Redis")
        
        # Ensure MongoDB connection is established
        await mongo_client.connect()
        logger.info("MongoDB connection established successfully")

        app.state.settings = settings
        app.state.redis_repository=container.redis.redis_repository()
        app.state.mongodb = mongo_client
        app.state.ai_model_client = container.openai.openai_client()
        app.state.ai_audio_client = container.openai.audio_client()
        

        yield
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise
        
    finally:
        # Close Redis connection
        await redis_instance.close()
        logger.info("Rate limiter connection closed")
        
        # Close MongoDB connection
        await mongo_client.disconnect()
        logger.info("MongoDB connection closed")
        
        # Close RabbitMQ connection
        logger.info("Closing RabbitMQ connection...")
        
        consumer.close_connection()
        consumer_thread.join()
        
        logger.info("RabbitMQ connection closed")