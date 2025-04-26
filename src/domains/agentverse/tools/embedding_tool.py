# src/core/agentverse/tools/embedding_tool.py

from typing import Any, Dict, ClassVar, List, Optional
import logging

from src.domains.agentverse.tools.base import BaseTool, ToolConfig, ToolExecutionError
from src.domains.agentverse.registries import tool_registry_instance as tool_registry

logger = logging.getLogger(__name__)

class EmbeddingToolConfig(ToolConfig):
    """Configuration for the EmbeddingTool"""
    # By default, don't auto-store embeddings
    upsert: bool = False
    collection: Optional[str] = None  # vectordb collection to upsert into
    namespace: Optional[str] = None   # optional namespace / metadata keyspace

@tool_registry.register(
    name="embed",
    description="Generate embeddings for text, and optionally upsert them into a vectordb.",
    version="1.0.0",
    metadata={"config_schema": "EmbeddingToolConfig"}
)
class EmbeddingTool(BaseTool):
    name: ClassVar[str] = "embed"
    version: ClassVar[str] = "1.0.0"
    required_dependencies: ClassVar[List[str]] = ["llm", "vectordb"]
    parameters: ClassVar[Dict[str, Any]] = {
        "text":       {"type": "string", "description": "Text to embed",      "required": True},
        "doc_id":     {"type": "string", "description": "ID for upsert",      "required": False},
        "metadata":   {"type": "object", "description": "Metadata for upsert", "required": False},
    }

    def __init__(
        self,
        config: Optional[EmbeddingToolConfig] = None,
        llm: Any = None,
        vectordb: Any = None
    ):
        super().__init__(config=config or EmbeddingToolConfig(), llm=llm, vectordb=vectordb)
        if not self.llm or not hasattr(self.llm, "get_embeddings_async"):
            raise ToolExecutionError("EmbeddingTool requires an async embedding client (`get_embeddings_async`)")
        if not self.vectordb:
            logger.warning("EmbeddingTool instantiated without a vectordb; upsert will be skipped")

    async def _run(
        self,
        text: str,
        doc_id: Optional[str]   = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        # 1) Generate embedding
        try:
            vector: List[float] = await self.llm.get_embeddings_async(text)
        except Exception as e:
            logger.error(f"EmbeddingTool failed to generate embeddings: {e}")
            raise ToolExecutionError(f"Embedding generation error: {e}")

        result: Dict[str, Any] = {"vector": vector}

        # 2) Optionally upsert to vectordb
        if self.config.upsert:
            coll = self.config.collection
            if not coll:
                raise ToolExecutionError("No collection specified for upsert")
            if not doc_id:
                raise ToolExecutionError("doc_id is required when upserting embeddings")
            # Prepare a single-document upsert
            await self.vectordb.upsert_many(
                collection=coll,
                documents=[{
                    "id":       doc_id,
                    "content":  text,
                    "vector":   vector,
                    "metadata": metadata or {}
                }]
            )
            result["upserted"] = {"collection": coll, "doc_id": doc_id}

        return result
