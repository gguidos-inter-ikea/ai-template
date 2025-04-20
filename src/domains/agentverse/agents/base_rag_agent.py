# Define a Base RAG Agent with essential functionalities
class BaseRagAgent:
    def __init__(self, vector_db, llm, prompt_template):
        self.vector_db = vector_db  # A vector database connector, e.g., FAISS or Pinecone
        self.llm = llm              # The language model engine
        self.prompt_template = prompt_template  # A prompt template string
    
    def retrieve(self, query):
        # Perform a similarity search against the vector DB
        retrieved_context = self.vector_db.search(query)
        return retrieved_context

    def generate(self, query, retrieved_context):
        # Fill in the prompt template with the query and the context
        prompt = self.prompt_template.format(query=query, context=retrieved_context)
        response = self.llm.generate(prompt)
        return response

    def process_query(self, query):
        context = self.retrieve(query)
        return self.generate(query, context)