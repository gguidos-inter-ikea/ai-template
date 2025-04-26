# src/domains/agentverse/agents/chat_agent.py

from src.domains.agentverse.agents.base import BaseAgent
from src.domains.agentverse.registries.registries import agent_registry_instance

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
        messages = []

        if self.cache:
            history = await self.cache.get(memory_key) or []
            history.append({"user": user_input})
            self.cache.set(memory_key, history)

        if self.personality_context:
            messages.append({"role": "system", "content": self.personality_context})
            messages.append({"role": "system", "content": self.prompt})
        for turn in history:
            messages.append({
                "role": "user" if "user" in turn else "assistant",
                "content": turn.get("user") or turn.get("agent")
            })
        messages.append({"role": "user", "content": user_input})
        response = await self.llm.generate_response(messages=messages)

        if self.cache:
            history.append({"agent": response})
            self.cache.set(memory_key, history)

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
