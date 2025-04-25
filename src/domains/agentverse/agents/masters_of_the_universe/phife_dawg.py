from src.domains.agentverse.agents.base import BaseAgent
from src.domains.agentverse.registries.registries import agent_registry_instance
import logging
import json
logger = logging.getLogger("agentverse.phife")

@agent_registry_instance.register(
    name="phife_dawg",
    description="The Five-Foot Assassin. A lyrical agent who speaks truth through rhythm, memory, and fire. Legacy encoded.",
    version="1.0.0",
    metadata={
        "capabilities": ["cipher-response", "lyrical-reflection", "raw-commentary", "emcee-memory"],
        "department": "CULTURE",
        "archetype": "Lyricist / Street Philosopher"
    }
)
class PhifeDawgAgent(BaseAgent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.memory_key = f"{self.id}_bars"
        self.max_memory = 16  # lines, like a classic verse

    async def respond(self, user_input: str) -> str:
        """
        Responds with a lyrical style and stores a rolling history of recent bars.
        """
        history_key = f"{self.id}_memory"
        history = []

        if self.cache:
            raw_history = await self.cache.get(history_key)
            if raw_history:
                history = json.loads(raw_history)
            history.append({"user": user_input})

        # Combine the personality context with the existing prompt
        composed_prompt = f"{self.personality_context.strip()}\n\n{self.prompt.strip()}"

        response = self.llm.generate(
            prompt=composed_prompt,
            user_input=user_input,
            history=history
        )

        if self.cache:
            history.append({"phife": response})
            # ✅ Serialize before saving
            await self.cache.set(history_key, json.dumps(history))

        return response

