from abc import ABC, abstractmethod
from typing import Any, Dict
from src.domains.agentverse.agents.personalities.utils.generate_personality_context import (
    generate_personality_context,
)
import logging

logger = logging.getLogger("agentverse.agents")

class BaseAgent(ABC):
    def __init__(
        self,
        id: str,
        creator: str,
        name: str,
        type: str,
        prompt: str,
        llm: Any,
        db: Any = None,
        cache: Any = None,
        vectordb: Any = None,
        messaging: Any = None,
        chat_url: str = None,
        personality_profile: str = None,
        personality: Any = None,
        dna_sequence: str = None,
    ):
        self.id = id
        self.creator = creator
        self.name = name
        self.type = type
        self.prompt = prompt
        self.llm = llm
        self.db = db
        self.cache = cache
        self.vectordb = vectordb
        self.messaging = messaging
        self.chat_url = chat_url,
        self.personality_profile = personality_profile
        self.personality = personality
        self.dna_sequence = dna_sequence
        self.personality_context = generate_personality_context(personality)

    @abstractmethod
    def respond(self, user_input: str) -> str:
        """Process an input and return a response."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Export all core agent attributes in a safe, readable dictionary format."""
        return {
            "id": self.id,
            "creator": self.creator,
            "name": self.name,
            "type": self.type,
            "prompt": self.prompt,
            "llm_type": getattr(self.llm, "model_name", str(self.llm)),
            "db_type": getattr(self.db, "name", None),
            "cache_type": getattr(self.cache, "type", None),
            "vectordb_type": getattr(self.vectordb, "type", None),
            "messaging_type": getattr(self.messaging, "channel", None),
            "chat_url": self.chat_url,
            "personality_profile": self.personality_profile,
            "personality": getattr(self.personality, "name", str(self.personality)) if self.personality else None,
            "dna_sequence": self.dna_sequence,
            "personality_context": self.personality_context,
        }
