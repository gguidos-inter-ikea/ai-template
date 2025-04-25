from typing import Optional
from src.domains.agentverse.entities.db import DBAgentPost
import logging
logger = logging.getLogger(__name__)

async def get_or_spawn_agent(
    request,
    agent_id: str,
    db_service,
    agent_service,
    cache,
    agent_registry: Optional[dict] = None
):
    agent_key = f"agent:{agent_id}:spawned"

    # Check if agent is already marked as spawned in Redis
    spawned_val = await cache.get(agent_key)
    is_spawned = spawned_val == "true"

    # Optional: check in local memory agent registry
    if is_spawned and agent_registry and agent_id in agent_registry:
        return agent_registry[agent_id]

    # If not found or not spawned, build from DB
    agent_data = await db_service.find_chat_agent(request, agent_id)
    db_agent = DBAgentPost(**agent_data)
    agent = await agent_service.build_agent(request=request, db_agent=db_agent)

    # Mark as spawned in Redis and optionally store in memory
    await agent.mark_spawned()
    if agent_registry is not None:
        agent_registry[agent_id] = agent

    return agent
