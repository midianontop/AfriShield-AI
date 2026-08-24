"""
AfriShield AI
African Offline Cybersecurity Intelligence Assistant
Version 3.3.0
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import streamlit as st


# =============================================================================
# LOGGING
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger("afrishield_ai")


# =============================================================================
# APP CONFIGURATION
# =============================================================================

APP_VERSION = "3.3.0"
APP_TAGLINE = "Offline African Cybersecurity Intelligence Platform"
CHALLENGE_TAG = "Africa Deep Tech Challenge 2026"
INCIDENT_LOG_PATH = "incident_logs.json"

USER_AVATAR = "🧑🏾"
ASSISTANT_AVATAR = "🛡️"


QUICK_PROMPTS = [
    "I think my WhatsApp was hacked",
    "Someone is asking for my BVN and OTP — is this a scam?",
    "What is phishing and how do I spot it?",
]


WELCOME_TIPS = [
    "Describe what happened in plain language.",
    "Mention whether money, passwords, OTPs, or personal IDs were requested.",
    "Do not share passwords, OTPs, PINs, BVN, NIN, or bank details.",
    "Always verify important security advice with official support channels.",
]


DO_NOT_SHARE_ITEMS = [
    "Passwords",
    "OTP codes",
    "BVN",
    "NIN",
    "ATM PIN",
    "Bank details",
]


# =============================================================================
# OPTIONAL MULTILINGUAL SUPPORT
# =============================================================================

try:
    from translations import get_translator, translate_message
    from language_detector import detect_language

    TRANSLATION_OK = True

except Exception:
    logger.exception("Translation system unavailable.")
    TRANSLATION_OK = False

    def get_translator():
        return None

    def translate_message(
        text: str,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "original": text,
            "language": "unknown",
            "translated": text,
            "matched_phrases": [],
        }

    def detect_language(text: str) -> str:
        return "unknown"


_translator = None


def get_app_translator():
    global _translator

    if _translator is None and TRANSLATION_OK:
        try:
            _translator = get_translator()
        except Exception:
            logger.exception("Could not initialize translator.")
            _translator = None

    return _translator


def safe_translate_message(text: str) -> Dict[str, Any]:

    if not TRANSLATION_OK:
        return {
            "original": text,
            "language": "unknown",
            "translated": text,
            "matched_phrases": [],
        }

    try:
        return translate_message(text)

    except Exception:
        logger.exception("Translation failed.")

        return {
            "original": text,
            "language": "unknown",
            "translated": text,
            "matched_phrases": [],
        }


def translate_for_user(
    text: str,
    language: str,
) -> str:

    if not text:
        return text

    if language in {"unknown", "english", ""}:
        return text

    translator = get_app_translator()

    if translator is None:
        return text

    try:
        return translator.translate_to_language(
            text,
            language,
        )

    except Exception:
        logger.exception("Response translation failed.")
        return text


# =============================================================================
# ENGINE IMPORTS
# =============================================================================

try:

    from retriever import search_documents

    RETRIEVER_OK = True

except Exception:

    logger.exception("Retriever unavailable.")

    RETRIEVER_OK = False

    def search_documents(query: str) -> List[str]:
        return []


try:

    from generate_answer import generate_answer

    LLAMA_OK = True

except Exception:

    logger.exception("LLM generator unavailable.")

    LLAMA_OK = False

    def generate_answer(
        question: str,
        context: str,
    ) -> str:

        return (
            "The offline AI response engine is currently unavailable. "
            "Please try again shortly."
        )


try:

    from threat_detector import analyze_threat

    THREAT_ENGINE_OK = True

except Exception:

    logger.exception("Threat detector unavailable.")

    THREAT_ENGINE_OK = False
    analyze_threat = None


try:

    from incident_response import get_incident_response

    INCIDENT_RESPONSE_OK = True

except Exception:

    logger.exception("Incident response unavailable.")

    INCIDENT_RESPONSE_OK = False

    def get_incident_response(
        threat_type: str,
    ) -> List[str]:
        return []


try:

    from incident_logger import save_incident

    INCIDENT_LOGGER_OK = True

except Exception:

    logger.exception("Incident logger unavailable.")

    INCIDENT_LOGGER_OK = False

    def save_incident(*args, **kwargs):
        return None


try:

    from scam_detector import detect_scam

    SCAM_ENGINE_OK = True

except Exception:

    logger.exception("Scam detector unavailable.")

    SCAM_ENGINE_OK = False

    def detect_scam(text: str):
        return None


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

def configure_page():

    st.set_page_config(
        page_title="AfriShield AI",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded",
    )


# =============================================================================
# SESSION STATE
# =============================================================================

def init_session_state():

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "_pending_question" not in st.session_state:
        st.session_state._pending_question = None


# =============================================================================
# INCIDENT COUNT
# =============================================================================

def load_incident_count() -> int:

    if not os.path.exists(INCIDENT_LOG_PATH):
        return 0

    try:

        with open(
            INCIDENT_LOG_PATH,
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        if isinstance(data, list):
            return len(data)

    except Exception:

        logger.exception(
            "Could not read incident log."
        )

    return 0


# =============================================================================
# UI HELPERS
# =============================================================================

def engine_status(
    name: str,
    ready: bool,
):

    if ready:
        st.success(f"🟢 {name} — Ready")

    else:
        st.error(f"🔴 {name} — Unavailable")


def render_header():

    st.title("🛡️ AfriShield AI")

    st.caption(
        "Offline African Cybersecurity Intelligence Platform"
    )

    st.divider()


def render_welcome():

    st.subheader(
        "👋 Start by describing a security concern"
    )

    st.caption(
        "Or choose one of the examples below."
    )

    columns = st.columns(3)

    for column, prompt in zip(
        columns,
        QUICK_PROMPTS,
    ):

        with column:

            if st.button(
                prompt,
                use_container_width=True,
            ):

                st.session_state._pending_question = prompt

                st.rerun()

    with st.expander(
        "💡 Quick guidance"
    ):

        for tip in WELCOME_TIPS:

            st.write(f"• {tip}")


# =============================================================================
# SIDEBAR
# =============================================================================

def render_sidebar():

    with st.sidebar:

        st.title("🛡️ AfriShield AI")

        st.caption(
            "Cybersecurity Intelligence"
        )

        st.divider()

        st.metric(
            "🚨 Incidents Logged",
            load_incident_count(),
        )

        st.divider()

        st.subheader("ENGINE STATUS")

        engine_status(
            "Translation / Language Layer",
            TRANSLATION_OK,
        )

        engine_status(
            "Threat Engine",
            THREAT_ENGINE_OK,
        )

        engine_status(
            "Scam Engine",
            SCAM_ENGINE_OK,
        )

        engine_status(
            "RAG Knowledge Base",
            RETRIEVER_OK,
        )

        engine_status(
            "LLM Response Generator",
            LLAMA_OK,
        )

        st.divider()

        st.subheader("📊 Session Statistics")

        messages = st.session_state.messages

        st.metric(
            "Messages",
            len(messages),
        )

        threats = sum(
            1
            for message in messages
            if message.get("threat")
        )

        st.metric(
            "Threats Detected",
            threats,
        )

        st.divider()

        if st.button(
            "🗑️ Clear Chat",
            use_container_width=True,
        ):

            st.session_state.messages = []

            st.rerun()

        if messages:

            st.download_button(
                "⬇️ Export Chat",

                data=json.dumps(
                    messages,
                    indent=2,
                    ensure_ascii=False,
                ),

                file_name=(
                    f"afrishield_chat_"
                    f"{datetime.now():%Y%m%d_%H%M%S}.json"
                ),

                mime="application/json",

                use_container_width=True,
            )

        st.divider()

        st.caption(
            f"AfriShield AI v{APP_VERSION}"
        )

        st.caption(
            CHALLENGE_TAG
        )


# =============================================================================
# ASSISTANT MESSAGE RENDERING
# =============================================================================

def render_assistant_message(
    message: Dict[str, Any],
):

    threat = (
        message.get("threat_display")
        or message.get("threat")
    )

    severity = message.get(
        "severity"
    )

    confidence = message.get(
        "confidence",
        0,
    )

    # -------------------------------------------------------------------------
    # Threat verdict
    # -------------------------------------------------------------------------

    if threat:

        st.warning(
            f"⚠️ {threat}"
        )

        if severity:

            st.write(
                f"**Severity:** {severity}"
            )

        st.write(
            f"**Confidence:** {confidence:.0f}%"
        )

        st.progress(
            min(
                max(
                    int(confidence),
                    0,
                ),
                100,
            )
        )

    # -------------------------------------------------------------------------
    # Scam alert
    # -------------------------------------------------------------------------

    scam = (
        message.get("scam_display")
        or message.get("scam")
    )

    if scam:

        st.error(
            f"🚨 Scam Alert: {scam}"
        )

        st.write(
            "**Never share:**"
        )

        for item in DO_NOT_SHARE_ITEMS:

            st.write(
                f"❌ {item}"
            )

    # -------------------------------------------------------------------------
    # Language / canonical interpretation
    # -------------------------------------------------------------------------

    canonical = message.get(
        "canonical_interpretation"
    )

    detected_language = message.get(
        "detected_language",
        "unknown",
    )

    if canonical and detected_language not in {
        "unknown",
        "english",
    }:

        with st.expander(
            "🌍 Canonical Interpretation"
        ):

            st.markdown(canonical)

    # -------------------------------------------------------------------------
    # Incident summary
    # -------------------------------------------------------------------------

    if message.get("incident_summary"):

        st.markdown(
            message["incident_summary"]
        )

    # -------------------------------------------------------------------------
    # Intent
    # -------------------------------------------------------------------------

    if message.get("intent_explanation"):

        st.markdown(
            message["intent_explanation"]
        )

    # -------------------------------------------------------------------------
    # Explainability
    # -------------------------------------------------------------------------

    if message.get("explainability"):

        with st.expander(
            "🔎 Why was this classified this way?"
        ):

            st.markdown(
                message["explainability"]
            )

    # -------------------------------------------------------------------------
    # Main response
    # -------------------------------------------------------------------------

    content = message.get(
        "content",
        "",
    )

    if content:

        st.markdown(content)

    # -------------------------------------------------------------------------
    # Recommendations
    # -------------------------------------------------------------------------

    recommendations = (
        message.get("recommendations_display")
        or message.get("recommendations")
        or []
    )

    if recommendations:

        st.subheader(
            "🛠 Recommended Actions"
        )

        for recommendation in recommendations:

            st.success(
                recommendation
            )

    # -------------------------------------------------------------------------
    # Analysis details
    # -------------------------------------------------------------------------

    if threat:

        with st.expander(
            "🔍 Threat Analysis Details"
        ):

            st.write(
                "**Intent:**",
                message.get("intent") or "—",
            )

            st.write(
                "**Matched Signals:**",
                message.get(
                    "matched_keywords"
                ) or [],
            )

            if message.get(
                "matched_phrases"
            ):

                st.write(
                    "**Matched Translation Phrases:**",
                    message.get(
                        "matched_phrases"
                    ),
                )


# =============================================================================
# CHAT HISTORY
# =============================================================================

def render_chat_history():

    for message in st.session_state.messages:

        role = message.get(
            "role",
            "assistant",
        )

        avatar = (
            ASSISTANT_AVATAR
            if role == "assistant"
            else USER_AVATAR
        )

        with st.chat_message(
            role,
            avatar=avatar,
        ):

            if role == "assistant":

                render_assistant_message(
                    message
                )

            else:

                st.write(
                    message.get(
                        "content",
                        "",
                    )
                )


# =============================================================================
# CORE AI PIPELINE
# =============================================================================

def analyze_user_message(
    question: str,
) -> Dict[str, Any]:

    # -------------------------------------------------------------------------
    # Language detection / translation
    # -------------------------------------------------------------------------

    translation = safe_translate_message(
        question
    )

    detected_language = (
        translation.get(
            "language",
            "unknown",
        )
        or "unknown"
    )

    translated_question = (
        translation.get(
            "translated",
            question,
        )
        or question
    )

    matched_phrases = translation.get(
        "matched_phrases",
        [],
    ) or []

    # -------------------------------------------------------------------------
    # Scam detection
    # -------------------------------------------------------------------------

    scam_result = None

    if SCAM_ENGINE_OK:

        try:

            scam_result = detect_scam(
                translated_question
            )

        except Exception:

            logger.exception(
                "Scam detection failed."
            )

    # -------------------------------------------------------------------------
    # Threat analysis
    # -------------------------------------------------------------------------

    threat_type = None
    severity = None
    confidence = 0.0
    intent = None
    intent_confidence = 0.0
    incident_type = None

    matched_keywords = []
    recommendations = []

    analysis = None

    if THREAT_ENGINE_OK:

        try:

            analysis = analyze_threat(
                translated_question
            )

        except Exception:

            logger.exception(
                "Threat analysis failed."
            )

    if (
        analysis is not None
        and analysis.category
        != "General Security Question"
    ):

        threat_type = analysis.category

        severity = analysis.severity.value

        confidence = analysis.confidence

        incident_type = (
            analysis.incident_type.value
        )

        intent = (
            analysis.user_intent.value
        )

        intent_confidence = (
            analysis.intent_confidence
        )

        matched_keywords = (
            analysis.matched_keywords
            or []
        )

        # -------------------------------------------------------------
        # Incident response
        # -------------------------------------------------------------

        if INCIDENT_RESPONSE_OK:

            try:

                recommendations = (
                    get_incident_response(
                        threat_type
                    )
                    or []
                )

            except Exception:

                logger.exception(
                    "Incident response failed."
                )

        # -------------------------------------------------------------
        # Incident logging
        # -------------------------------------------------------------

        if INCIDENT_LOGGER_OK:

            try:

                save_incident(
                    translated_question,
                    threat_type,
                    severity,
                    confidence,
                )

            except Exception:

                logger.exception(
                    "Incident logging failed."
                )

    # -------------------------------------------------------------------------
    # RAG retrieval
    # -------------------------------------------------------------------------

    documents = []

    if RETRIEVER_OK:

        try:

            documents = (
                search_documents(
                    translated_question
                )
                or []
            )

        except Exception:

            logger.exception(
                "Document retrieval failed."
            )

    context = "\n\n".join(
        documents
    )

    if threat_type:

        context += (
            "\n\nThreat Analysis:"
            f"\nCategory: {threat_type}"
            f"\nSeverity: {severity}"
            f"\nConfidence: {confidence:.0f}%"
            "\n\nRecommended Response:"
            f"\n{recommendations}"
        )

    # -------------------------------------------------------------------------
    # LLM generation
    # -------------------------------------------------------------------------

    try:

        answer = generate_answer(
            translated_question,
            context,
        )

    except Exception:

        logger.exception(
            "Answer generation failed."
        )

        answer = (
            "I could not generate a full "
            "response right now. Please try again."
        )

    # -------------------------------------------------------------------------
    # Incident summary
    # -------------------------------------------------------------------------

    incident_summary = None

    if threat_type:

        incident_summary = (
            "### Incident Summary\n\n"
            f"**Category:** {threat_type}\n\n"
            f"**Severity:** {severity}\n\n"
            f"**Confidence:** {confidence:.0f}%"
        )

        if matched_keywords:

            incident_summary += (
                "\n\n**Signals:** "
                + ", ".join(
                    matched_keywords
                )
            )

    # -------------------------------------------------------------------------
    # Intent explanation
    # -------------------------------------------------------------------------

    intent_explanation = None

    if intent:

        intent_explanation = (
            "### Detected Intent\n\n"
            f"**Intent:** {intent}\n\n"
            f"**Confidence:** "
            f"{intent_confidence:.0f}%"
        )

        if matched_keywords:

            intent_explanation += (
                "\n\n**Matched terms:** "
                + ", ".join(
                    matched_keywords
                )
            )

    # -------------------------------------------------------------------------
    # Explainability
    # -------------------------------------------------------------------------

    explainability = None

    if matched_keywords:

        explainability = (
            "**Why this was flagged:**\n\n"
            f"- Matched signals: "
            f"{', '.join(matched_keywords)}\n"
            f"- Confidence: "
            f"{confidence:.0f}%\n"
            f"- Incident type: "
            f"{incident_type or 'Unknown'}"
        )

    # -------------------------------------------------------------------------
    # Canonical interpretation
    # -------------------------------------------------------------------------

    canonical_interpretation = (
        "### Canonical Interpretation\n\n"
        f"**User input:** {question}\n\n"
        f"**Canonical meaning:** "
        f"{translated_question}"
    )

    if matched_phrases:

        canonical_interpretation += (
            "\n\n**Matched phrases:** "
            + ", ".join(
                matched_phrases
            )
        )

    # -------------------------------------------------------------------------
    # Scam block
    # -------------------------------------------------------------------------

    response_parts = []

    if scam_result:

        response_parts.append(
            "### Scam Alert\n\n"
            f"**Scam Type:** {scam_result}\n\n"
            "**Never share:**\n"
            + "\n".join(
                f"- {item}"
                for item in DO_NOT_SHARE_ITEMS
            )
        )

    response_parts.append(
        answer
    )

    final_answer = "\n\n".join(
        part
        for part in response_parts
        if part
    )

    # -------------------------------------------------------------------------
    # Translate response
    # -------------------------------------------------------------------------

    translated_recommendations = (
        recommendations
    )

    translated_threat = threat_type

    translated_scam = scam_result

    if detected_language not in {
        "unknown",
        "english",
        "",
    }:

        translator = (
            get_app_translator()
        )

        if translator:

            try:

                final_answer = (
                    translate_for_user(
                        final_answer,
                        detected_language,
                    )
                )

                translated_recommendations = [
                    translator.translate_to_language(
                        item,
                        detected_language,
                    )
                    for item in recommendations
                ]

                if threat_type:

                    translated_threat = (
                        translator.translate_to_language(
                            threat_type,
                            detected_language,
                        )
                    )

                if scam_result:

                    translated_scam = (
                        translator.translate_to_language(
                            scam_result,
                            detected_language,
                        )
                    )

            except Exception:

                logger.exception(
                    "Response translation failed."
                )

    # -------------------------------------------------------------------------
    # Return assistant message
    # -------------------------------------------------------------------------

    return {

        "role": "assistant",

        "content": final_answer,

        "threat": threat_type,

        "threat_display": translated_threat,

        "severity": severity,

        "confidence": confidence,

        "recommendations": recommendations,

        "recommendations_display":
            translated_recommendations,

        "scam": scam_result,

        "scam_display": translated_scam,

        "intent": intent,

        "incident_summary":
            incident_summary,

        "intent_explanation":
            intent_explanation,

        "canonical_interpretation":
            canonical_interpretation,

        "explainability":
            explainability,

        "matched_keywords":
            matched_keywords,

        "matched_phrases":
            matched_phrases,

        "detected_language":
            detected_language,

        "translated_question":
            translated_question,

        "user_input":
            question,
    }


# =============================================================================
# MAIN
# =============================================================================

def main():

    configure_page()

    init_session_state()

    render_sidebar()

    render_header()

    render_chat_history()

    if not st.session_state.messages:

        render_welcome()

    pending_question = (
        st.session_state.pop(
            "_pending_question",
            None,
        )
    )

    typed_question = st.chat_input(
        "Describe a cyber incident or ask a security question..."
    )

    question = (
        pending_question
        or typed_question
    )

    if not question or not question.strip():

        st.caption(
            "AfriShield AI provides general security "
            "guidance. Verify important actions through "
            "official channels."
        )

        return

    # -------------------------------------------------------------------------
    # User message
    # -------------------------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message(
        "user",
        avatar=USER_AVATAR,
    ):

        st.write(question)

    # -------------------------------------------------------------------------
    # AI response
    # -------------------------------------------------------------------------

    with st.chat_message(
        "assistant",
        avatar=ASSISTANT_AVATAR,
    ):

        with st.spinner(
            "🛡️ AfriShield AI analyzing..."
        ):

            assistant_message = (
                analyze_user_message(
                    question
                )
            )

        render_assistant_message(
            assistant_message
        )

    st.session_state.messages.append(
        assistant_message
    )


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()