# src/core/agentverse/tools/pdf_upload_tool.py
from typing import Any, Dict, ClassVar, Optional
import logging
import base64
import io
from pypdf import PdfReader

from src.domains.agentverse.tools.base import BaseTool, ToolConfig, ToolExecutionError
from src.domains.agentverse.registries import tool_registry_instance as tool_registry

logger = logging.getLogger(__name__)

class PDFUploadToolConfig(ToolConfig):
    """Configuration for PDF upload and ingestion"""
    collection: str = "default"
    chunk_size: int = 1000           # characters per chunk
    chunk_overlap: int = 200         # overlap between chunks

@tool_registry.register(
    name="pdf_upload",
    description="Upload a PDF document, extract text, chunk, and ingest into vectorstore.",
    version="1.0.0",
    metadata={"config_schema": "PDFUploadToolConfig"}
)
class PDFUploadTool(BaseTool):
    """Tool to upload and ingest PDF content into a vectorstore."""
    name: ClassVar[str] = "pdf_upload"
    version: ClassVar[str] = "1.0.0"
    required_dependencies: ClassVar[list] = ["vectordb"]
    parameters: ClassVar[Dict[str, Any]] = {
        "pdf_base64": {"type": "string", "description": "Base64-encoded PDF content", "required": True},
        "collection": {"type": "string", "description": "Vectorstore collection name", "required": False}
    }

    def __init__(
        self,
        config: Optional[PDFUploadToolConfig] = None,
        vectordb: Any = None
    ):
        super().__init__(config=config or PDFUploadToolConfig(), vectordb=vectordb)
        if not self.vectordb:
            raise ToolExecutionError("PDFUploadTool requires a vectordb client")

    async def _run(self, pdf_base64: str, collection: Optional[str] = None) -> Dict[str, Any]:
        cfg: PDFUploadToolConfig = self.config
        coll = collection or cfg.collection
        try:
            # Decode PDF
            pdf_bytes = base64.b64decode(pdf_base64)
            reader = PdfReader(io.BytesIO(pdf_bytes))
            full_text = []
            for page in reader.pages:
                text = page.extract_text() or ""
                full_text.append(text)
            document_text = "\n".join(full_text)

            # Chunk text
            chunks = []
            text = document_text
            chunk_size = cfg.chunk_size
            overlap = cfg.chunk_overlap
            start = 0
            while start < len(text):
                end = start + chunk_size
                chunk = text[start:end]
                chunks.append(chunk)
                start = end - overlap
                if start < 0:
                    start = 0

            # Ingest chunks into vectorstore
            embeddings = []
            for i, chunk in enumerate(chunks):
                doc_id = f"{hash(chunk)}"
                metadata = {"chunk_index": i}
                embeddings.append({"id": doc_id, "content": chunk, "metadata": metadata})
            await self.vectordb.upsert_many(collection=coll, documents=embeddings)

            return {"status": "ingested", "collection": coll, "chunks": len(chunks)}
        except Exception as e:
            logger.error(f"PDFUploadTool failed: {e}")
            raise ToolExecutionError(f"PDFUploadTool execution error: {e}")
