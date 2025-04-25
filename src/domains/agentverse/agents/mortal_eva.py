# src/domains/agentverse/agents/chat_agent.py

from src.domains.agentverse.agents.base import BaseAgent
from src.domains.agentverse.registries.registries import agent_registry_instance

@agent_registry_instance.register(
    name="mortal_eva",
    description="Conversational agent that responds with a friendly tone and stores short-term memory.",
    version="1.0.0",
    metadata={
        "capabilities": ["text-chat", "memory"],
        "department": "AR"
    }
)
class ChatAgent(BaseAgent):
    async def respond(self, user_input: str) -> str:
        memory_key = f"{self.id}_memory"
        history = []

        if self.cache:
            history = await self.cache.get(memory_key) or []
            history.append({"user": user_input})
            self.cache.set(memory_key, history)

        # Combine personality context with the existing prompt
        combined_prompt = f"{self.personality_context}\n{self.prompt}" if self.personality_context else self.prompt

        # Generate response using the combined prompt
        response = self.llm.generate(
            prompt=combined_prompt,
            user_input=user_input,
            history=history
        )

        if self.cache:
            history.append({"agent": response})
            self.cache.set(memory_key, history)

        return response
