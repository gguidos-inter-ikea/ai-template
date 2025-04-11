from redis.asyncio import Redis
from typing import Optional, List
import logging

logger = logging.getLogger("redis_client")

class RedisClient:
    """Class to encapsulate Redis operations."""

    def __init__(self, host: str, port: int, db: int, password: Optional[str] = None):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.client: Optional[Redis] = None

    async def connect(self) -> None:
        """Connect to the Redis server."""
        if not self.client:
            self.client = await Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info(f"Connected to Redis at {self.host}:{self.port}")

    async def disconnect(self) -> None:
        """Disconnect from the Redis server."""
        if self.client:
            await self.client.close()
            logger.info("Disconnected from Redis.")
            self.client = None

    async def get(self, key: str) -> Optional[str]:
        """Get a value from Redis by key."""
        if not self.client:
            raise ConnectionError("Redis client is not connected.")
        return await self.client.get(key)

    async def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """Set a key-value pair in Redis with an optional expiration time."""
        if not self.client:
            raise ConnectionError("Redis client is not connected.")
        return await self.client.set(key, value, ex=expire)

    async def delete(self, key: str) -> int:
        """Delete a key from Redis."""
        if not self.client:
            raise ConnectionError("Redis client is not connected.")
        return await self.client.delete(key)

    async def ping(self) -> bool:
        """Ping the Redis server to check connection status."""
        if not self.client:
            raise ConnectionError("Redis client is not connected.")
        return await self.client.ping() == "PONG"

    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in Redis.
        
        Returns:
            True if the key exists, False otherwise.
        """
        if not self.client:
            raise ConnectionError("Redis client is not connected.")
        # Redis EXISTS returns the number of keys existing (0 or 1 in this case)
        return (await self.client.exists(key)) > 0

    async def scan_keys(self, pattern: str, count: int = 10) -> List[str]:
        """
        Scan and return keys matching a given pattern.
        
        Args:
            pattern: The pattern to match keys.
            count: The number of keys to return per iteration (hint for Redis).
            
        Returns:
            A list of keys matching the pattern.
        """
        if not self.client:
            raise ConnectionError("Redis client is not connected.")
        keys = []
        async for key in self.client.scan_iter(match=pattern, count=count):
            keys.append(key)
        return keys

    def __getattr__(self, name: str):
        """
        Forward attribute lookups to the Redis client.
        This will ensure that methods like `script_load` can be accessed.
        """
        if self.client:
            return getattr(self.client, name)
        raise AttributeError(f"'RedisClient' object has no attribute '{name}'")
