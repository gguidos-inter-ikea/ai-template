# src/domains/agentverse/agents/chat_agent.py

from src.domains.agentverse.agents.base import BaseAgent
from src.domains.agentverse.registries.registries import agent_registry_instance
import json
@agent_registry_instance.register(
    name="chat",
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

        # 🔒 Safely load history from Redis
        if self.cache:
            raw = await self.cache.get(memory_key)
            try:
                history = json.loads(raw) if raw else []
            except json.JSONDecodeError:
                history = []

            history.append({"user": user_input})

        # 🧠 Compose prompt with personality context
        composed_prompt = f"{self.personality_context.strip()}\n\n{self.prompt.strip()}"

        response = self.llm.generate(
            prompt=composed_prompt,
            user_input=user_input,
            history=history
        )

        # 🔐 Safely save updated history
        if self.cache:
            history.append({"agent": response})
            await self.cache.set(memory_key, json.dumps(history))

        return response
    
    
    async def _update_memory(self, memory_key, entry):
        MAX_RAW_TURNS = 10

        history = await self.cache.get(memory_key) or []
        history.append(entry)
        # If too long, compress the oldest turns
        if len(history) > MAX_RAW_TURNS * 2:
            # Summarize the first half, keep the second half raw
            raw_to_summarize = history[:MAX_RAW_TURNS]
            summary = await self.tools["summarize"].execute(
                text="\\n".join(f"{m['user'] if 'user' in m else m['agent']}" for m in raw_to_summarize),
                style="bullets"
            )
            history = [{"summary": summary.result}] + history[MAX_RAW_TURNS:]
        await self.cache.set(memory_key, history)
