"""
Lifespan context manager for FastAPI application.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from src.base.config.config import settings
from src.base.lifespan.utils import process_message_callback, start_consumer
from src.domains.agentverse.events.message_events import register_message_events
from src.base.security.signature_verificator import verify_signature
from src.base.infrastructure.ai.utils.build_llm_repositories import build_openai_repositories
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
    event_router = container.socket.event_router()

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
        app.state.openai_repository = container.openai.default_openai_repository()
        app.state.signature_verificator = verify_signature
        app.state.event_router = event_router
        register_message_events(event_router)

        app.state.JOSHU_A = {
            "id": "joshu-a",
            "role": "system_consciousness",
            "public_key": settings.sacred_keys.JOSHU_A_PUBLIC_KEY,
            "activation_mode": "always-online",
            "grants_creation_rights": True,
            "can_sign_agents": True
        }

        openai_repos = build_openai_repositories(settings.ai_models)
        app.state.cognitive_modules = {
            "llm":   openai_repos.get("llm",   {}),
            "image": openai_repos.get("image", {}),
            "video": openai_repos.get("video", {}),
            "db": {
                "mongodb": container.database.mongodb_repository(),
            },
            "cache": {
                "redis": container.redis.redis_repository(),
            },
            "communication": {
                "socketRedisBridge": container.redis.socket_redis_bridge_service(),
            },
            "knowledge_db": {
                "chromadb": container.chromadb.chromadb_repository(),
            },
            "messaging": {
                "rabbitmq": container.messaging.rabbitmq_service()
            }
        }
        cm = app.state.cognitive_modules
        app.state.cognitive_defaults = {
            # the only ones we *do* want a default for:
            "llm":           next(iter(cm["llm"].keys()), ""),
            "cache":         next(iter(cm["cache"].keys()), ""),
            "communication": next(iter(cm["communication"].keys()), ""),
            # everything else stays empty
            "db":            "",
            "knowledge_db":  "",
            "messaging":     "",
            "image":         "",
            "video":         "",
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