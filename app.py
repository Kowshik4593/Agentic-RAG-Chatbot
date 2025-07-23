# app.py

import streamlit as st
import uuid
from agents.coordinator_agent import CoordinatorAgent

st.set_page_config(page_title="Agentic RAG Chatbot", layout="wide")

st.title("🤖 Agentic RAG Chatbot")
st.write("This chatbot uses a multi-agent system to answer questions from your documents.")

# Initialize the CoordinatorAgent in session state
if "coordinator" not in st.session_state:
    st.session_state.coordinator = CoordinatorAgent()

# --- Sidebar for Document Upload ---
with st.sidebar:
    st.header("1. Upload Documents")
    uploaded_files = st.file_uploader(
        "Upload PDF, DOCX, TXT, CSV, or PPTX files",
        type=['pdf', 'docx', 'txt', 'csv', 'pptx'],
        accept_multiple_files=True
    )
    
    # app.py (partial code)

    if st.button("Process Documents") and uploaded_files:
        with st.status("IngestionAgent: Processing documents...", expanded=True) as status:
            # We don't need a trace_id here for now, but will use it later
            
            # The IngestionAgent now needs the actual file objects
            result = st.session_state.coordinator.handle_ingestion(uploaded_files)
            
            if result.get("status") == "SUCCESS":
                # Store the extracted text in the session state
                st.session_state.processed_text = result['extracted_text']
                status.update(label="✅ Ingestion Complete!", state="complete")
                st.success(f"Processed {len(result['processed_files'])} files.")
            else:
                status.update(label="❌ Ingestion Failed!", state="error")
                st.error(result.get("error", "An unknown error occurred."))

# --- Main Chat Interface ---
st.header("2. Ask Questions")
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# app.py (partial code, end of the file)

if prompt := st.chat_input("What are the key KPIs?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Coordinator is thinking..."):
            trace_id = str(uuid.uuid4())
            # The coordinator now returns a dictionary with the answer and sources
            response = st.session_state.coordinator.handle_query(prompt, trace_id)
            
            # Display the final answer
            st.markdown(response["final_answer"])

            # Display the source context in an expander
            if response["context_chunks"]:
                with st.expander("Show Sources"):
                    for i, chunk in enumerate(response["context_chunks"]):
                        st.info(f"Source {i+1}:\n\n" + chunk)

    # Add the full response (answer + sources) to the message history
    st.session_state.messages.append({
        "role": "assistant", 
        "content": response["final_answer"],
        "context": response["context_chunks"]
    })