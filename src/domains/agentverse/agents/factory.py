import uuid
from typing import Any, Callable
from dataclasses import dataclass
from fastapi import Request
import re
import unicodedata
from src.domains.agentverse.entities.agent import (
    Agent,
    AgentConfig,
    BaseAgentConfig
)
from src.domains.agentverse.entities.db import (
    DBAgentPost
)
from src.domains.agentverse.agents.base import BaseAgent
from src.domains.agentverse.logging.logger import log_evangelion_bay

import logging

logger = logging.getLogger(__name__)

@dataclass
class CognitiveResources:
    llm: Any
    db: Any
    cache: Any
    vectordb: Any
    messaging: Any


class AgentFactory:
    ...
    def __init__(
            self,
            synchronize_agent: Callable,
            resolve_personality: Callable,
            generate_dna_sequence: Callable,
            get_agent_class: Callable
        ):
        self.synchronize_agent = synchronize_agent
        self.resolve_personality = resolve_personality
        self.generate_dna_sequence = generate_dna_sequence
        self.get_agent_class = get_agent_class

    def create_agent(self, agent_config: AgentConfig) -> Agent:
        try:
            log_evangelion_bay(f"[🧬 EVA DNA CONSTRUCTION] Initiating prototype '{agent_config.name}' at EVANGELION BAY")

            agent_id = str(uuid.uuid4())
            log_evangelion_bay(f"[🔗 IDENTIFIER] Genetic ID sequence bound: {agent_id}")

            chat_url = f"/chat/{agent_id}"
            log_evangelion_bay(f"[🌐 NEURAL CHANNEL] Communication interface established: {chat_url}")

            log_evangelion_bay("[🧬 DNA SYNTHESIS] EVA genetic code synthesis in progress...")
            dna_sequence = self.generate_dna_sequence(agent_config)
            log_evangelion_bay(f"[🧬 DNA SEQUENCE] Genetic code synthesized: {dna_sequence}")

            log_evangelion_bay("[🧬 PERSONALITY SYNTHESIS] EVA personality traits detected — initiating trait fusion sequence...")
            personality = self.resolve_personality(agent_config)
            log_evangelion_bay(f"[🧬 PERSONALITY BINDING] EVA personality traits bound to '{personality.name}'")

            agent = Agent(
                id=agent_id,
                name=agent_config.name,
                system_name=self.to_system_name(agent_config.name),
                prompt=agent_config.prompt,
                type=agent_config.type,
                chat_url=chat_url,
                llm_type=agent_config.llm_type,
                db_type=agent_config.db_type,
                cache_type=agent_config.cache_type,
                knowledge_db_type=agent_config.knowledge_db_type,
                messaging_type=agent_config.messaging_type,
                personality=personality,
                personality_profile=agent_config.personality_profile,
                dna_sequence=dna_sequence
            )

            log_evangelion_bay(f"[✅ COMPLETE] EVA '{agent.name}' is now blueprint-ready for activation")
            return agent

        except Exception as e:
            log_evangelion_bay(f"[🔥 EVA CREATION FAILURE] Encountered issue during agent creation for '{agent_config.name}': {str(e)}")
            raise

    async def build_agent(self, request: Request, db_agent: DBAgentPost) -> BaseAgent:
        log_evangelion_bay(f"[⚙️ EVA CONSTRUCTION] Initializing assembly process for '{db_agent.agent_name}'")

        agent_cognitive_resources = self._resolve_components(request, db_agent)
        log_evangelion_bay(f"[⚙️ EVA CONSTRUCTION] Core assembly in progress for '{db_agent.agent_name}'")
        agent_class = self.get_agent_class(db_agent.agent_type)
        

        agent_config = BaseAgentConfig(
            id=db_agent.agent_id,
            creator=db_agent.creator,
            name=db_agent.agent_name,
            system_name=db_agent.agent_system_name,
            type=db_agent.agent_type,
            prompt=db_agent.agent_prompt,
            personality=db_agent.agent_personality,
            llm=agent_cognitive_resources.llm,
            db=agent_cognitive_resources.db,
            cache=agent_cognitive_resources.cache,
            vectordb=agent_cognitive_resources.vectordb,
            messaging=agent_cognitive_resources.messaging,
            chat_url=db_agent.agent_chat_url,
            personality_profile=db_agent.agent_personality_profile,
            dna_sequence=db_agent.agent_dna_sequence
        )

        agent = agent_class(**agent_config.dict())
        await agent.mark_spawned()

        log_evangelion_bay(f"[⚙️ EVA CONSTRUCTION] Core assembly for '{db_agent.agent_name}' completed")
        log_evangelion_bay(f"""
            [⚙️ EVA CONSTRUCTION] :: {db_agent.agent_name}
            → Internal frame: synchronized
            → Neural scaffold: bonded
            → LCL Levels Stabilized
            → EVA personality profile: {db_agent.agent_personality_profile}
            → Soul protocol hash: {db_agent.agent_dna_sequence[:8]}...
            ✓ EVA '{db_agent.agent_name}' now bound to Soul Grid.
        """)

        
        return agent
    
    def synchronize_agent(self, agent_blueprint: dict) -> BaseAgent:
        log_evangelion_bay("[🧠 SYNCHRONIZATION] Establishing neural sync with EVA blueprint...")
        agent_class = self.synchronize_agent.get(agent_blueprint["type"])
        log_evangelion_bay("[🔗 SYNCHRONIZATION] Neural pattern successfully synchronized")
        return agent_class(**agent_blueprint)

    def _resolve_components(self, request: Request, db_agent: DBAgentPost) -> CognitiveResources:
        log_evangelion_bay("[🔍 COGNITIVE LINKING] Resolving component matrix for EVA's operational memory...")

        llm = request.app.state.cognitive_modules["llm"].get(db_agent.agent_llm_type)
        db = request.app.state.cognitive_modules["db"].get(db_agent.agent_db_type)
        cache = request.app.state.cognitive_modules["cache"].get(db_agent.agent_cache_type)
        vectordb = request.app.state.cognitive_modules["knowledge_db"].get(db_agent.agent_knowledge_db_type)
        messaging = request.app.state.cognitive_modules["messaging"].get(db_agent.agent_messaging_type)

        log_evangelion_bay(
            f"[🧠 COMPONENTS LINKED] Cognitive matrix mapped — "
            f"LLM: {bool(llm)}, DB: {bool(db)}, Cache: {bool(cache)}, VectorDB: {bool(vectordb)}, Messaging: {bool(messaging)}"
        )

        return CognitiveResources(
            llm=llm,
            db=db,
            cache=cache,
            vectordb=vectordb,
            messaging=messaging
        )



    def to_system_name(self, name: str) -> str:
        """
        Normalize and convert a human-readable agent name to a clean, system-friendly identifier.

        Steps:
        - Normalize Unicode characters to ASCII (NFKD)
        - Remove non-alphanumeric characters except spaces
        - Replace spaces with underscores
        - Lowercase everything

        Example:
            "Ingvar Kamprád!" → "ingvar_kamprad"
            "  Customized EVA  " → "customized_eva"
        """
        # Normalize to NFKD form and strip diacritics
        normalized = unicodedata.normalize("NFKD", name)
        ascii_str = normalized.encode("ascii", "ignore").decode("ascii")

        # Remove unwanted symbols (keep letters, numbers, and spaces)
        cleaned = re.sub(r"[^a-zA-Z0-9 ]+", "", ascii_str)

        # Replace spaces with underscores and lower the case
        system_name = cleaned.strip().lower().replace(" ", "_")
        
        return system_name