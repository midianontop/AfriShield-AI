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

question = st.text_input(
    "Enter your question:"
)

# ====================================
# Ask Button
# ====================================

if st.button("Ask"):

    if question.strip():

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

            # Save user message
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": question
                }
            )

            # Save assistant message
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer
                }
            )

# ====================================
# Chat History
# ====================================

st.markdown("---")

for msg in st.session_state.messages:

    if msg["role"] == "user":

        st.markdown("### 👤 You")
        st.write(msg["content"])

    else:

        st.markdown("### 🛡️ AI Assistant")
        st.write(msg["content"])

    st.markdown("---")