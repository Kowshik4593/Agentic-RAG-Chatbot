# agents/retrieval_agent.py

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

class RetrievalAgent:
    def __init__(self):
        print("RetrievalAgent initialized.")
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        self.embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = None

    def store(self, text: str):
        """
        Chunks the text, creates embeddings, and stores them in a FAISS vector store.
        """
        if not text:
            print("RetrievalAgent: No text to store.")
            return

        print("RetrievalAgent: Chunking and embedding text...")
        chunks = self.text_splitter.split_text(text)
        
        # Create a FAISS vector store from the text chunks
        self.vector_store = FAISS.from_texts(texts=chunks, embedding=self.embeddings_model)
        print("RetrievalAgent: Vector store created successfully.")

    def run(self, mcp_message: dict):
        """
        Receives a query, searches the vector store for relevant chunks.
        """
        print("RetrievalAgent: Running...")
        query = mcp_message["payload"]["query"]

        if self.vector_store is None:
            return {
                "sender": "RetrievalAgent",
                "receiver": "CoordinatorAgent",
                "type": "ERROR_RESPONSE",
                "payload": {"error": "Vector store is not initialized. Please process documents first."}
            }
            
        print(f"RetrievalAgent: Searching for relevant chunks for query: '{query}'")
        
        # Perform similarity search
        docs = self.vector_store.similarity_search(query, k=3) # Get top 3 most relevant chunks
        
        retrieved_chunks = [doc.page_content for doc in docs]

        return {
            "sender": "RetrievalAgent",
            "receiver": "CoordinatorAgent",
            "type": "CONTEXT_RESPONSE",
            "payload": {"top_chunks": retrieved_chunks}
        }