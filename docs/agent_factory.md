# AgentFactory

The `AgentFactory` class orchestrates the lifecycle of agents in the AgentVerse ecosystem. It provides a factory-based system to create, build, and synchronize intelligent agents that are equipped with various cognitive resources (LLMs, databases, caches, and vector stores).

Each agent is treated like a virtual being—an EVA—assembled from a blueprint and linked with its necessary intelligence and memory.

---

## 📦 Class: `AgentFactory`

### `create_agent(agent_config: AgentConfig) -> Agent`
Creates a new agent blueprint with a unique ID and the initial metadata.

- **Args**:
  - `agent_config` (`AgentConfig`): The agent's configuration definition.
- **Returns**:
  - `Agent`: An agent record containing identifiers and configuration (but no live resources).

---

### `build_agent(request: Request, db_agent: DBAgentPost) -> BaseAgent`
Builds a fully operational agent using stored metadata and application-level resources.

- **Args**:
  - `request` (`Request`): FastAPI request, provides access to stateful resources.
  - `db_agent` (`DBAgentPost`): Agent definition from persistent storage.
- **Returns**:
  - `BaseAgent`: A ready-to-use agent with all components wired.

---

### `synchronize_agent(agent_blueprint: dict) -> BaseAgent`
Reconstructs an agent from a blueprint dictionary.

- **Args**:
  - `agent_blueprint` (`dict`): All necessary parameters to recreate the agent.
- **Returns**:
  - `BaseAgent`: An instantiated, operational agent.

---

### `_resolve_components(request: Request, db_agent: DBAgentPost) -> CognitiveResources`
Internal method that pulls the required cognitive resources from app state based on the agent’s configuration.

- **Args**:
  - `request`: FastAPI request context with access to application services.
  - `db_agent`: Agent's stored configuration.
- **Returns**:
  - `CognitiveResources`: Dataclass wrapping resolved components (LLM, DB, Cache, VectorDB).

---

## 🧠 Supporting Class: `CognitiveResources`

A dataclass that holds cognitive components for an agent:
```python
@dataclass
class CognitiveResources:
    llm: Any
    db: Any
    cache: Any
    vectordb: Any
```
This structure allows agents to interact with databases, perform inference via LLMs, cache data, and reason over vector-based memory.

---

## 🗒️ Design Notes

- Inspired by biological and mechanical analogies (EVA units, neural links, etc.)
- Fully DI-compatible and modular
- Supports future agent types via registry + factory

---

## 🔁 Lifecycle Analogy

- **create_agent**: Define identity and type → 🧬 DNA / Blueprint
- **build_agent**: Assemble systems and memory → 🏭 Mech build
- **synchronize_agent**: Reboot from stored mind → 💾 Neural sync