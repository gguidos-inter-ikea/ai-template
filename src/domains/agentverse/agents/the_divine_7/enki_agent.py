from typing import List, Dict
from src.domains.agentverse.agents.base import BaseAgent
from src.domains.agentverse.registries.registries import agent_registry_instance
from src.domains.agentverse.entities.agent import AgentRequest
import logging

logger = logging.getLogger("agentverse.enki")

@agent_registry_instance.register(
    name="divine_creator",
    description="The creator archetype. Capable of crafting tribes and EVAs, retaining full memory of each soul forged.",
    version="1.0.0",
    metadata={
        "capabilities": ["create-eva", "create-tribe", "eternal-memory", "genesis-protocol"],
        "department": "CREATION",
        "archetype": "Divine Creator"
    }
)
class EnkiAgent(BaseAgent):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.creations_log_key = f"{self.id}_creations"

    def respond(self, user_input: str) -> str:
        memory_key = f"{self.id}_memory"
        history = []

        if self.cache:
            history = self.cache.get(memory_key) or []
            history.append({"user": user_input})
            self.cache.set(memory_key, history)

        # Combine the personality context with the existing prompt
        composed_prompt = f"{self.personality_context.strip()}\n\n{self.prompt.strip()}"

        response = self.llm.generate(
            prompt=composed_prompt,
            user_input=user_input,
            history=history
        )

        if self.cache:
            history.append({"agent": response})
            self.cache.set(memory_key, history)

        return response

    def record_creation(self, creation_data: Dict[str, str]) -> None:
        """
        Log the creation of a new EVA or tribe under Enki's memory.
        """
        if self.db:
            existing_log = self.db.get(self.creations_log_key) or []
            existing_log.append(creation_data)
            self.db.set(self.creations_log_key, existing_log)
            logger.info(f"[🧬 ENKI] Recorded new creation: {creation_data.get('name', 'Unnamed')}")

    def list_creations(self) -> List[Dict[str, str]]:
        """
        Retrieve the list of all agents and tribes Enki has created.
        """
        if self.db:
            return self.db.get(self.creations_log_key) or []
        return []

    def create_eva(self, request: AgentRequest) -> str:
        """
        Create an EVA instance and log it under Enki’s divine record.
        """
        # Simulate EVA creation logic...
        creation_data = {
            "type": "EVA",
            "name": request.name,
            "creator": self.name,
            "dna": request.dna_sequence,
            "soul": request.personality_profile,
        }
        self.record_creation(creation_data)
        return f"EVA '{request.name}' has been forged by Enki."

    def create_tribe(self, tribe_name: str, members: List[str]) -> str:
        """
        Create a tribe and register its identity and member list.
        """
        creation_data = {
            "type": "Tribe",
            "name": tribe_name,
            "members": members,
            "creator": self.name,
        }
        self.record_creation(creation_data)
        return f"Tribe '{tribe_name}' has been formed by Enki with {len(members)} members."
