from dependency_injector import containers, providers
import aioredis
from src.base.config.config import settings
from src.base.repositories.redis_impl import RedisRepositoryImpl
from src.base.infrastructure.db.redis.redis_client import RedisClient

class RedisContainer(containers.DeclarativeContainer):
    """
    Container for Redis-related dependencies.
    """
    # Redis client
    redis_client = providers.Resource(
        aioredis.Redis,
        host=settings.cache.redis_host,
        port=settings.cache.redis_port,
        db=settings.cache.redis_db,
        password=settings.cache.redis_password,
        encoding="utf-8",
        decode_responses=True,
    )

    redis_repository = providers.Resource(
        RedisRepositoryImpl,
        redis_client = redis_client
    )