import streamlit as st
from retriever import search_documents
from generate_answer import generate_answer

# ====================================
# Page Configuration
# ====================================

st.set_page_config(
    page_title="African Cybersecurity AI Assistant",
    page_icon="🛡️",
    layout="wide"
)

# ====================================
# Session State
# ====================================

if "messages" not in st.session_state:
    st.session_state.messages = []

# ====================================
# Sidebar
# ====================================

with st.sidebar:

    st.title("🛡️ About")

    st.write("""
    **African Cybersecurity AI Assistant**

    Built by: Midian

    Features:
    - Offline AI
    - Retrieval-Augmented Generation (RAG)
    - ChromaDB Vector Search
    - Llama 3.2 Local LLM
    - Cybersecurity Knowledge Base
    - African Cybersecurity Awareness
    """)

    st.markdown("---")

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ====================================
# Main Page
# ====================================

st.title("🛡️ African Cybersecurity AI Assistant")

st.write(
    "Ask cybersecurity questions and get answers from the local knowledge base."
)

# ====================================
# Display Chat History
# ====================================

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ====================================
# Chat Input
# ====================================

question = st.chat_input(
    "Ask a cybersecurity question..."
)

# ====================================
# Process Question
# ====================================

if question:

    # Show user message immediately
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):
        st.write(question)

    with st.spinner("Searching knowledge base and generating answer..."):

        # Retrieve relevant chunks
        results = search_documents(question)

        # Combine retrieved chunks
        context = "\n\n".join(results)

        # Generate answer
        answer = generate_answer(
            question,
            context
        )

    # Save assistant response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    with st.chat_message("assistant"):
        st.write(answer)