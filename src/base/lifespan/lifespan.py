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
        app.state.mongodb = mongo_client
        app.state.redis_repository=container.redis.redis_repository()
        app.state.openai_repository = container.openai.openai_repository()
        app.state.chromadb_repository = container.chromadb.chromadb_repository()

        app.state.cognitive_modules = {
            "llm": {
                "openai": container.openai.openai_repository()
            },
            "db": {
                "mongodb": container.database.mongodb_repository(),
            },
            "cache": {
                "redis": container.redis.redis_repository(),
            },
            "knowledge_db": {
                "chromadb": container.chromadb.chromadb_repository(),
            },
            "messaging": {
                "rabbitmq": container.messaging.rabbitmq_service()
            }
        }
        

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