# src/core/agentverse/tools/rag_tool.py
from typing import Any, Dict, ClassVar, Optional
import logging

from src.domains.agentverse.tools.base import BaseTool, ToolConfig, ToolExecutionError
from src.domains.agentverse.registries import tool_registry_instance as tool_registry

logger = logging.getLogger(__name__)

class RAGToolConfig(ToolConfig):
    """Configuration for Retrieval-Augmented Generation Tool"""
    max_context_length: int = 2000  # max chars of retrieved context to include

@tool_registry.register(
    name="rag",
    description="Retrieval-Augmented Generation: fetch relevant context and generate answers.",
    version="1.0.0",
    metadata={"config_schema": "RAGToolConfig"}
)
class RAGTool(BaseTool):
    """Tool that performs retrieval-augmented generation using vectordb and LLM."""
    name: ClassVar[str] = "rag"
    version: ClassVar[str] = "1.0.0"
    description: ClassVar[str] = (
        "Retrieve top-k documents from a vectorstore and generate an answer grounded in them."
    )
    required_dependencies: ClassVar[list] = ["llm", "vectordb"]
    parameters: ClassVar[Dict[str, Any]] = {
        "query":      {"type":"string","description":"User question to answer","required":True},
        "collection": {"type":"string","description":"Name of the vectordb collection","required":True},
        "top_k":      {"type":"integer","description":"Number of docs to retrieve","default":5}
    }

    def __init__(
        self,
        config: Optional[RAGToolConfig] = None,
        llm: Any = None,
        vectordb: Any = None,
    ):
        super().__init__(config=config or RAGToolConfig(), llm=llm, vectordb=vectordb)
        if not self.llm:
            raise ToolExecutionError("RAGTool requires an llm client")
        if not self.vectordb:
            raise ToolExecutionError("RAGTool requires a vectordb client")

    async def _run(self, query: str, collection: str, top_k: int = 5) -> Dict[str, Any]:
        # Retrieve documents
        docs = await self.vectordb.search(
            collection=collection,
            query=query,
            limit=top_k
        )
        # Assemble context string
        context = "\n\n".join(doc.content for doc in docs)
        if len(context) > self.config.max_context_length:
            # Keep only the last slice
            context = context[-self.config.max_context_length:]

        # Build prompt for LLM
        prompt = (
            f"You are an expert assistant. Use the following context to answer the question."
            f"\n\nContext:\n{context}\n\nQuestion: {query}\nAnswer:"
        )
        try:
            response = await self.llm.generate_response(prompt=prompt)
            return {
                "answer": response.content,
                "sources": [doc.metadata for doc in docs]
            }
        except Exception as e:
            logger.error(f"RAGTool generation failed: {e}")
            raise ToolExecutionError(f"RAGTool execution error: {e}")
