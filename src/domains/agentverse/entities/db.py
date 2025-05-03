from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from src.domains.agentverse.entities.tools.tool_spec import ToolSpec

class DBAgentPost(BaseModel):
    creator: str
    agent_id: str
    agent_name: str
    agent_system_name: str
    agent_type: str
    agent_prompt: str
    agent_llm_type: str
    agent_db_type: Optional[str] = None
    agent_cache_type: Optional[str] = None
    agent_knowledge_db_type: Optional[str] = None
    agent_messaging_type: Optional[str] = None
    agent_personality: Dict[str, Any] 
    agent_access_mode: Optional[str] = "public"  # Options: "public", "commander", "ritual", "guardian", "offline"
    agent_public_key: Optional[str] = None  # distributed for verification
    agent_private_key: Optional[str] = None # kept encrypted, used to sign memory, DNA merges
    agent_whitelist_users: Optional[List[str]] = None  # Usernames or session keys allowed
    agent_blacklist_users: Optional[List[str]] = None  # Users explicitly denied
    agent_tools: List[ToolSpec]
    agent_dna_sequence: str
    agent_chat_url: str
    tools: Optional[List[str]] = None  # List of tool names