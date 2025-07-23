# agents/coordinator_agent.py
import json
from .ingestion_agent import IngestionAgent
from .retrieval_agent import RetrievalAgent
from .llm_response_agent import LLMResponseAgent

class CoordinatorAgent:
    def __init__(self):
        self.ingestion_agent = IngestionAgent()
        self.retrieval_agent = RetrievalAgent()
        self.llm_response_agent = LLMResponseAgent()
        print("CoordinatorAgent initialized.")

    def _create_mcp_message(self, sender, receiver, msg_type, payload, trace_id):
        """Helper to create a structured MCP message."""
        return {
            "sender": sender,
            "receiver": receiver,
            "type": msg_type,
            "trace_id": trace_id,
            "payload": payload
        }

    def handle_query(self, query: str, trace_id: str):
        """
        Coordinates the full RAG process for a user query.
        """
        print(f"Coordinator handling query with trace_id: {trace_id}")

        # 1. Retrieval
        retrieval_payload = {"query": query}
        retrieval_msg = self._create_mcp_message(
            "CoordinatorAgent", "RetrievalAgent", "RETRIEVAL_REQUEST", retrieval_payload, trace_id
        )
        print(f"MCP --> {json.dumps(retrieval_msg, indent=2)}")
        context_chunks = self.retrieval_agent.run(retrieval_msg)

        # 2. LLM Response Generation
        llm_payload = {
            "query": query,
            "top_chunks": context_chunks["payload"]["top_chunks"]
        }
        llm_msg = self._create_mcp_message(
            "CoordinatorAgent", "LLMResponseAgent", "GENERATION_REQUEST", llm_payload, trace_id
        )
        print(f"MCP --> {json.dumps(llm_msg, indent=2)}")
        final_response_message = self.llm_response_agent.run(llm_msg)
        
        # Return the entire payload, which now contains the answer and the context
        return final_response_message["payload"]
    # agents/coordinator_agent.py (partial code)

    def handle_ingestion(self, files: list):
        """
        Coordinates the document ingestion process.
        """
        print(f"Coordinator handling ingestion...")
        
        # We no longer need to create an MCP message here, just call the agent directly.
        # The agent will handle the parsing and, in the future, embedding.
        ingestion_result = self.ingestion_agent.run(files)
        
        if ingestion_result["status"] == "SUCCESS":
            # In the next step, the coordinator will pass the text to the
            # retrieval agent to be chunked and stored in the vector DB.
            print("Coordinator: Ingestion successful. Storing text for retrieval.")
            self.retrieval_agent.store(ingestion_result["extracted_text"])
        
        return ingestion_result