import streamlit as st
from retriever import search_documents
from generate_answer import generate_answer
from threat_detector import detect_threat
from incident_response import get_incident_response
from confidence import get_confidence
from incident_logger import save_incident
from scam_detector import detect_scam

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
    - Threat Detection
    - Scam Detection
    - Incident Response Recommendations
    - Confidence Score
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

        if msg["role"] == "assistant":

            # Threat Information

            if msg["threat"]:

                st.write(
                    f"🛡️ Threat Type: {msg['threat']}"
                )

                st.write(
                    f"⚠️ Severity: {msg['severity']}"
                )

                st.write(
                    f"📊 Confidence: {msg['confidence']}"
                )

            # Scam Information

            if msg["scam_type"]:

                st.error(
                    f"🚨 Scam Alert: {msg['scam_type']}"
                )

            # AI Answer

            st.write(
                msg["content"]
            )

            # Recommendations

            if msg["recommendations"]:

                st.write(
                    "### Recommended Actions"
                )

                for action in msg["recommendations"]:

                    st.write(
                        f"✅ {action}"
                    )

        else:

            st.write(
                msg["content"]
            )

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

    # Save User Message

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):
        st.write(question)

    with st.spinner(
        "Analyzing and generating answer..."
    ):

        # ====================================
        # Scam Detection
        # ====================================

        scam_type = detect_scam(
            question
        )

        # ====================================
        # Threat Detection
        # ====================================

        threat_keywords = [
            "attack",
            "hacked",
            "hack",
            "malware",
            "virus",
            "ransomware",
            "phishing",
            "breach",
            "compromised",
            "fraud",
            "scam"
        ]

        is_threat = any(
            word in question.lower()
            for word in threat_keywords
        )

        if is_threat:

            threat_type, severity = detect_threat(
                question
            )

            confidence = get_confidence(
                severity
            )

            recommendations = (
                get_incident_response(
                    threat_type
                )
            )

            save_incident(
                question,
                threat_type,
                severity,
                confidence
            )

        else:

            threat_type = None
            severity = None
            confidence = None
            recommendations = []

        # ====================================
        # Retrieve Context
        # ====================================

        results = search_documents(
            question
        )

        context = "\n\n".join(
            results
        )

        # ====================================
        # Generate AI Answer
        # ====================================

        ai_answer = generate_answer(
            question,
            context
        )

        # ====================================
        # Scam Warning
        # ====================================

        if scam_type:

            ai_answer = f"""
🚨 Scam Alert Detected

Scam Type: {scam_type}

{ai_answer}

⚠️ Be careful.

Do not share:
- Passwords
- OTP Codes
- ATM Card Details
- Bank Details
- Personal Information
"""

    # ====================================
    # Save Assistant Message
    # ====================================

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": ai_answer,
            "threat": threat_type,
            "severity": severity,
            "confidence": confidence,
            "recommendations": recommendations,
            "scam_type": scam_type
        }
    )

    # ====================================
    # Display Assistant Response
    # ====================================

    with st.chat_message("assistant"):

        if threat_type:

            st.write(
                f"🛡️ Threat Type: {threat_type}"
            )

            st.write(
                f"⚠️ Severity: {severity}"
            )

            st.write(
                f"📊 Confidence: {confidence}"
            )

        if scam_type:

            st.error(
                f"🚨 Scam Alert: {scam_type}"
            )

        st.write(
            ai_answer
        )

        if recommendations:

            st.write(
                "### Recommended Actions"
            )

            for action in recommendations:

                st.write(
                    f"✅ {action}"
                )