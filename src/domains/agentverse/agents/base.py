from abc import ABC, abstractmethod
from typing import Any, Dict
from src.domains.agentverse.agents.personalities.utils.generate_personality_context import (
    generate_personality_context,
)
from src.domains.agentverse.logging.logger import log_existencial_index
import asyncio
import logging

logger = logging.getLogger("agentverse.agents")
class BaseAgent(ABC):
    def __init__(
        self,
        id: str,
        creator: str,
        name: str,
        system_name: str,
        type: str,
        prompt: str,
        llm: Any,
        db: Any = None,
        cache: Any = None,
        vectordb: Any = None,
        commbridge: Any = None,
        messaging: Any = None,
        chat_url: str = None,
        personality_profile: str = None,
        personality: Any = None,
        dna_sequence: str = None,
        # wallets: List[Wallet] = None
    ):
        log_existencial_index(
            f"[🧬 EVA DNA CONSTRUCTION] Final Assembling of Artificial Human Evangelium '{name}'"
        )
        self.id = id
        self.creator = creator
        self.name = name
        self.system_name = system_name
        self.type = type
        self.prompt = prompt
        self.llm = llm
        self.db = db
        self.cache = cache
        self.vectordb = vectordb
        self.commbridge = commbridge
        self.messaging = messaging
        self.chat_url = chat_url  # ← fixed here
        self.personality_profile = personality_profile
        self.personality = personality
        self.dna_sequence = dna_sequence
        self.personality_context = generate_personality_context(personality)

        # self.wallets = wallets  # ← attribute name matches below
        log_existencial_index(
            f"[🧬 EVA DNA CONSTRUCTION] EVA '{name}' is ready for activation."
        )

    @abstractmethod
    def respond(self, user_input: str) -> str:
        """Process an input and return a response."""
        pass

    async def mark_spawned(self):
        self.spawned = True
        if self.cache:
            await self.cache.set(f"agent:{self.id}:spawned", "true", expiration=3600)
            
    async def sleep(self):
        self.spawned = False
        if self.cache:
            await self.cache.delete(f"agent:{self.id}:spawned")

    async def remember(self, key: str, value: Any):
        if self.cache:
            await self.cache.set(f"agent:{self.id}:{key}", value)

    async def recall(self, key: str, default: Any = None) -> Any:
        if self.cache:
            result = await self.cache.get(f"agent:{self.id}:{key}")
            return result if result is not None else default
        return default

    async def forget(self, key: str):
        if self.cache:
            await self.cache.delete(f"agent:{self.id}:{key}")

    async def is_spawned(self) -> bool:
        if self.cache:
            value = await self.cache.get(f"agent:{self.id}:spawned")
            return value == "true"
        return self.spawned  # fallback to in-memory flag
    
    async def listen_for_name(self):
        """
        Subscribes this agent to Redis messages sent to its own name channel via the communication bridge.
        """
        if not self.commbridge or not hasattr(self.commbridge, "redis_repository"):
            logger.warning(f"[⚠️] Agent {self.name} has no communication bridge with Redis access.")
            return

        channel = f"agent:{self.system_name.lower()}"
        logger.info(f"[👂] {self.system_name} is now listening on Redis channel: {channel}")

        async def message_handler():
            async for message in self.commbridge.redis_repository.subscribe_channel(channel):
                logger.info(f"[📩] {self.name} received message: {message}")
                await self.handle_message(message)

        asyncio.create_task(message_handler())

    async def handle_message(self, message: str):
        """
        Hook to be overridden by agents to define how they handle incoming messages.
        """
        logger.info(f"[🤖] {self.name} received but did not handle message: {message}")

    def on_event(self, event_name: str):
        return event_name

    def to_dict(self) -> Dict[str, Any]:
        """Export all core agent attributes in a safe, readable dictionary format."""
        return {
            "id": self.id,
            "creator": self.creator,
            "name": self.name,
            "system_name": self.system_name,
            "type": self.type,
            "prompt": self.prompt,
            "llm_type": getattr(self.llm, "model_name", str(self.llm)),
            "db_type": getattr(self.db, "name", None),
            "cache_type": getattr(self.cache, "type", None),
            "vectordb_type": getattr(self.vectordb, "type", None),
            "commbridge_type": getattr(self.commbridge, "type", None),
            "messaging_type": getattr(self.messaging, "channel", None),
            "chat_url": self.chat_url,
            "personality_profile": self.personality_profile,
            "personality": getattr(self.personality, "name", str(self.personality)) if self.personality else None,
            "dna_sequence": self.dna_sequence,
            "personality_context": self.personality_context,
            # "wallets": self.wallets
        }
