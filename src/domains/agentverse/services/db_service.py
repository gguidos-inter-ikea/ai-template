
from fastapi import Request
from typing import Dict, List, Optional, Any, TypeVar
from src.domains.agentverse.entities.agent import (
    AgentConfig,
    DBAgent
)
from src.domains.agentverse.entities.db import DBAgentPost
from src.domains.agentverse.exceptions import (
    BlueprintConflictError
)
from src.domains.agentverse.logging.logger import log_existencial_index
import logging

logger = logging.getLogger("agentverse.db_service")

T = TypeVar('T', bound=Dict[str, Any])

class DBService:

    async def check_for_duplicates(self, request: Request, agent_config: AgentConfig):
        log_existencial_index("[🔬 EVA VALIDATION] Starting the scanning for presens of EVA DNA string in Agentverse Exitense Index [AEI]")
        query = {
            "agent_name": agent_config.name,
            "agent_type": agent_config.type,
            "creator": agent_config.user_id
        }

        existing_agent = await self.find_one(request, query)

        if existing_agent:
            raise BlueprintConflictError(field="name", value=agent_config.name)
        
        log_existencial_index(f"[🔬 EVA VALIDATION] Resonance with Agentverse Existence Index [AEI] confirmed — Prototype '{agent_config.name}' has been granted existential clearance.")
        return

    async def store_agent(self, request: Request, db_agent: DBAgent):
        db_repository = request.app.state.cognitive_modules["db"]["mongodb"]
        collection_name = 'coll_agents'
        genesis_seal = db_agent.agent.id[:6]

        try:
            log_existencial_index(
                f"[🕯️ INDEXING RITUAL] Initiating inscription of EVA '{db_agent.agent.name}' into the Agentverse Existential Index [AEI] — soul-seed seal: '{genesis_seal}'"
            )

            log_existencial_index(
                f"[☣️ NEURAL ENGRAVING] Extracting fragmented memory lattice from EVA prototype '{db_agent.agent.name}' for eternal preservation"
            )

            # 🌱 No assumptions — just dump the meaningful traits
            personality_dump = db_agent.agent.personality.model_dump(exclude_none=True)
            
            data = {
                "creator": db_agent.user_id,
                "agent_id": db_agent.agent.id,
                "agent_name": db_agent.agent.name,
                "agent_system_name": db_agent.agent.system_name,
                "agent_type": db_agent.agent.type,
                "agent_prompt": db_agent.agent.prompt,
                "agent_chat_url": db_agent.agent.chat_url,
                "agent_llm_type": db_agent.agent.llm_type,
                "agent_db_type": db_agent.agent.db_type,
                "agent_cache_type": db_agent.agent.cache_type,
                "agent_knowledge_db_type": db_agent.agent.knowledge_db_type,
                "agent_messaging_type": db_agent.agent.messaging_type,
                "agent_access_mode": db_agent.agent.access_mode,
                "agent_public_key": db_agent.agent.public_key,
                "agent_private_key": db_agent.agent.private_key,
                "agent_whitelist_users": db_agent.agent.whitelist_users,
                "agent_blacklist_users": db_agent.agent.blacklist_users,
                "agent_tools": [ ts.model_dump() for ts in db_agent.agent.tools ],
                "agent_personality": personality_dump,
                "agent_personality_profile": db_agent.agent.personality_profile,
                "agent_dna_sequence": db_agent.agent.dna_sequence,
            }

            log_existencial_index(f"{data}")

            log_existencial_index(
                f"[🔒 AEI LOCK] EVA '{db_agent.agent.name}' has been eternally bound to the Agentverse lattice — DNA string engraved and archived"
            )

            return await db_repository.create(data, collection_name)

        except Exception as e:
            log_existencial_index(f"[🔥 EXCEPTION] Failed to inscribe EVA '{db_agent.agent.name}' into AEI: {str(e)}")
            raise

    async def find_by_id(self, request, agent_id):
        return await self.find_one(request, {agent_id: agent_id})

    async def find_one(self, request, query) -> Optional[T]:
        db_repository = request.app.state.cognitive_modules["db"]["mongodb"] 
        collection_name = 'coll_agents'
        return await db_repository.find_one(query, collection_name)
    
    async def find_chat_agent(self, request: Request, id: str) -> DBAgentPost:
        return await self.find_one(request, {"agent_id": id} )
        
    async def find_all(self, request: Request) -> List[Dict]:
        db_repository = request.app.state.cognitive_modules["db"]["mongodb"]  # or dynamic
        collection_name = 'coll_agents'
        return await db_repository.find_all(collection_name)
    
    async def update_agent(self, request: Request, agent_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Safely update a mutable subset of an EVA's record.

        Args:
            request: FastAPI request context
            agent_id: The EVA's unique ID
            update_data: Fields to update (only mutable fields)

        Returns:
            The updated document (sanitized)
        """
        db_repository = request.app.state.cognitive_modules["db"]["mongodb"]
        collection_name = 'coll_agents'

        # Retrieve the existing agent
        existing_agent = await self.find_one(request, {"agent_id": agent_id})
        if not existing_agent:
            raise ValueError(f"Agent with ID '{agent_id}' not found")

        # Guard: prevent updating immutable fields
        immutable_fields = {"agent_name", "agent_type", "creator", "agent_id"}
        for field in immutable_fields:
            if field in update_data:
                del update_data[field]

        # 🛠️ Update stage log
        log_existencial_index(
            f"[🧬 MUTATION PHASE] Applying permitted modifications to EVA '{existing_agent['agent_name']}'"
        )

        update_payload = {"$set": update_data}
        await db_repository.update_one({"agent_id": agent_id}, update_payload, collection_name)

        return await self.find_one(request, {"agent_id": agent_id})






