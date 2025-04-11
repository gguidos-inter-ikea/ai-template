from typing import List
from src.base.infrastructure.ai.openai_client import OpenAIClient

def create_embedding_function() -> callable:
    """
    Returns a callable embedding function that accepts a string input and returns its embedding vector.
    """
    # Retrieve the OpenAIClient instance from your DI container.
    from src.base.dependencies.di_container import Container  # Your DI container
    container = Container()
    openai_client: OpenAIClient = container.openai.openai_client()
    
    def embedding_function(text: str) -> List[float]:
        # Use the synchronous get_embeddings method.
        return openai_client.get_embeddings(text)
    
    return embedding_function
