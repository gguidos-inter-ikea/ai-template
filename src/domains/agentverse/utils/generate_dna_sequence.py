import hashlib
import json
from src.domains.agentverse.entities.agent import AgentConfig

def generate_dna_sequence(agent_config: AgentConfig) -> str:
    dna_data = {
        "agent_name": agent_config.name,
        "agent_type": agent_config.type,
        "creator": agent_config.user_id
    }
    dna_string = json.dumps(dna_data, sort_keys=True)
    return hashlib.sha256(dna_string.encode()).hexdigest()
