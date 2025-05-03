# File: src/tools/migrate_personalities.py

from typing import Dict, Type
from pydantic import BaseModel
from src.domains.agentverse.entities.agent_soul_protocol import AgentSoulProtocol
from src.domains.agentverse.entities.agent_soul_protocol_parts.identity_profile import IdentityProfile
from src.domains.agentverse.entities.agent_soul_protocol_parts.cognitive_profile import CognitiveProfile
from src.domains.agentverse.entities.agent_soul_protocol_parts.culinary_profile import CulinaryProfile
from src.domains.agentverse.entities.agent_soul_protocol_parts.cultural_profile import CulturalProfile
from src.domains.agentverse.entities.agent_soul_protocol_parts.economic_profile import EconomicProfile
from src.domains.agentverse.entities.agent_soul_protocol_parts.expression_profile import ExpressionProfile
from src.domains.agentverse.entities.agent_soul_protocol_parts.personal_profile import PersonalProfile
from src.domains.agentverse.entities.agent_soul_protocol_parts.sensory_profile import SensoryProfile
from src.domains.agentverse.entities.agent_soul_protocol_parts.simulation_profile import SimulationProfile
from src.domains.agentverse.entities.agent_soul_protocol_parts.spiritual_profile import SpiritualProfile
from src.domains.agentverse.entities.agent_soul_protocol_parts.agent_soul_protocol_metadata import AgentSoulProfileMetadata

from src.domains.agentverse.registries import personality_registry_instance
import os


import importlib.util

def import_all_personality_archetypes():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agents", "personalities"))

    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                full_path = os.path.join(root, file)

                # Convert path to module format for import (e.g., src.domains.agentverse.agents.personalities.the_divine_7.enki)
                rel_path = os.path.relpath(full_path, os.path.join(os.path.dirname(__file__), "../.."))
                module_name = rel_path.replace("/", ".").replace("\\", ".").replace(".py", "")

                print(f"📦 Importing: {module_name}")
                spec = importlib.util.spec_from_file_location(module_name, full_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)




PROFILE_FIELD_MAP = {
    "identity_profile": IdentityProfile,
    "cognitive_profile": CognitiveProfile,
    "culinary_profile": CulinaryProfile,
    "cultural_profile": CulturalProfile,
    "economic_profile": EconomicProfile,
    "expression_profile": ExpressionProfile,
    "personal_profile": PersonalProfile,
    "sensory_profile": SensoryProfile,
    "simulation_profile": SimulationProfile,
    "spiritual_profile": SpiritualProfile,
    "agent_soul_profile_metadata": AgentSoulProfileMetadata,
}


def migrate_flat_personality(personality_cls: Type[AgentSoulProtocol]) -> Type[AgentSoulProtocol]:
    instance = personality_cls()
    flat_data = instance.model_dump(exclude_none=True)
    profiles: Dict[str, BaseModel] = {}

    for profile_name, profile_cls in PROFILE_FIELD_MAP.items():
        profile_fields = profile_cls.model_fields.keys()
        profile_data = {k: v for k, v in flat_data.items() if k in profile_fields}
        if profile_data:
            profiles[profile_name] = profile_cls(**profile_data)

    new_class_name = f"Modular{personality_cls.__name__}"
    ModularPersonality = type(
        new_class_name,
        (AgentSoulProtocol,),
        {
            "__doc__": f"Auto-migrated modular version of `{personality_cls.__name__}`",
            **profiles
        }
    )
    return ModularPersonality

def migrate_all_personalities():
    migrated = {}

    print("🔍 Inspecting registry...")
    print("Available attributes:", dir(personality_registry_instance))

    try:
        registry = getattr(personality_registry_instance, "_registry", None)
        if registry is None:
            raise AttributeError("Registry object has no '_registry' attribute.")

        print(f"✅ Found _registry with {len(registry)} entries")
        for name, cls in registry.items():
            if not isinstance(cls, type) or not issubclass(cls, AgentSoulProtocol):
                continue
            print(f"🔄 Migrating personality: {name} ({cls.__name__})")
            try:
                new_cls = migrate_flat_personality(cls)
                migrated[name] = new_cls
            except Exception as e:
                print(f"❌ Error migrating {name}: {e}")
        return migrated

    except Exception as e:
        print(f"❌ Could not inspect registry: {e}")
        return {}



def write_code_to_file(cls: Type[AgentSoulProtocol], name: str, output_dir: str):
    """
    Writes a .py file with the modular class definition.
    """
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"{name.lower()}_modular.py")

    lines = [
        "# Auto-generated modular AgentSoulProtocol class\n",
        "from src.domains.agentverse.entities.agent_soul_protocol import AgentSoulProtocol",
    ]
    print(f"🔍 Registry attributes: {dir(personality_registry_instance)}")
    print(f"📦 Registry class: {type(personality_registry_instance)}")

    for profile_name in PROFILE_FIELD_MAP:
        lines.append(
            f"from src.domains.agentverse.entities.agent_soul_protocol_parts.{profile_name} import {PROFILE_FIELD_MAP[profile_name].__name__}"
        )

    lines.append(f"\n\nclass {cls.__name__}(AgentSoulProtocol):")
    for profile_name in PROFILE_FIELD_MAP:
        profile = getattr(cls, profile_name, None)
        if profile:
            repr_profile = repr(profile)
            lines.append(f"    {profile_name}: {PROFILE_FIELD_MAP[profile_name].__name__} = {repr_profile}")

    with open(filename, "w") as f:
        f.write("\n".join(lines))

    print(f"📝 Saved: {filename}")

if __name__ == "__main__":
    import_all_personality_archetypes()
    migrated_classes = migrate_all_personalities()
    for name, cls in migrated_classes.items():
        print(f"✅ Migrated: {name} -> {cls.__name__}")
        write_code_to_file(cls, name, output_dir="src/domains/agentverse/entities/migrated_personalities")
