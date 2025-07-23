# agents/llm_response_agent.py

import streamlit as st
from groq import Groq

class LLMResponseAgent:
    def __init__(self):
        print("LLMResponseAgent initialized.")
        try:
            # Initialize the Groq client, which automatically uses the secret
            self.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        except Exception as e:
            st.error(f"Failed to initialize Groq client. Make sure your API key is in .streamlit/secrets.toml. Error: {e}")
            self.client = None

    def _create_prompt(self, query: str, context_chunks: list):
        """
        Creates a detailed prompt for the LLM, instructing it to answer based ONLY on the provided context.
        """
        prompt_template = f"""
        **Instruction:** You are a helpful assistant. Your task is to answer the user's query based *only* on the provided context.
        Do not use any external knowledge. If the answer is not found in the context, state that clearly.
        Be concise and directly answer the question.

        **Context:**
        ---
        {"\n---\n".join(context_chunks)}
        ---

        **Query:** {query}

        **Answer:**
        """
        return prompt_template

    def run(self, mcp_message: dict):
        """
        Forms the final LLM query using the retrieved context and generates the answer.
        """
        if not self.client:
            return { "payload": {"final_answer": "LLM client not initialized."} }

        print("LLMResponseAgent: Running...")
        query = mcp_message["payload"]["query"]
        context = mcp_message["payload"]["top_chunks"]

        # If no context was found, return a specific message
        if not context:
            return {
                "payload": {"final_answer": "I could not find any relevant information in the uploaded documents to answer your question."}
            }

        prompt = self._create_prompt(query, context)

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192", # A fast and capable model
            )
            final_answer = chat_completion.choices[0].message.content
        except Exception as e:
            print(f"LLMResponseAgent: Error calling Groq API: {e}")
            final_answer = "I encountered an error while trying to generate a response."

        return {
            "sender": "LLMResponseAgent",
            "receiver": "CoordinatorAgent",
            "type": "FINAL_ANSWER",
            "payload": {
                "final_answer": final_answer,
                "context_chunks": context # Pass the original context back
            }
        }