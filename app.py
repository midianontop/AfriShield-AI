"""
================================================================================
  AfriShield AI
  African Offline Cybersecurity Intelligence Assistant

  Main Streamlit Application
================================================================================

  Author  : Midian
  Version : 3.3.0
================================================================================
"""

from __future__ import annotations

import json
import logging
import os
import textwrap
from datetime import datetime
from typing import Any, Dict, List, Optional

import streamlit as st

# =============================================================================
# RETRIEVER WARM-UP
# =============================================================================

@st.cache_resource(show_spinner=False)
def initialize_retriever():
    """
    Load the embedding model and ChromaDB once.

    Streamlit keeps this resource in memory so subsequent
    questions do not reload the embedding model.
    """
    try:
        retriever_ready()
        return True
    except Exception:
        logging.exception("Retriever warm-up failed.")
        return False

# ==============================================================================
# LOGGING
# ==============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("afrishield_ai")

try:
    from translations import get_translator, translate_message
    from language_detector import detect_language
    TRANSLATION_OK = True
except Exception:
    logger.exception("Translation modules failed to load; multilingual support is disabled.")
    TRANSLATION_OK = False

    def get_translator():
        return None

    def translate_message(text: str, language: Optional[str] = None) -> Dict[str, Any]:
        return {
            "original": text,
            "language": "unknown",
            "translated": text,
            "matched_phrases": [],
        }

    def detect_language(text: str) -> str:
        return "unknown"


# ==============================================================================
# CONFIGURATION
# ==============================================================================

APP_VERSION = "3.3.0"
APP_TAGLINE = "Offline African Cybersecurity Intelligence Platform"
CHALLENGE_TAG = "Africa Deep Tech Challenge 2026"
INCIDENT_LOG_PATH = "incident_logs.json"

_app_translator = None


def get_app_translator():
    global _app_translator
    if _app_translator is None and TRANSLATION_OK:
        try:
            _app_translator = get_translator()
        except Exception:
            logger.exception("Failed to initialize translator on demand.")
            _app_translator = None
    return _app_translator


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
        logger.exception("Translation failed for this message.")
        return {
            "original": text,
            "language": "unknown",
            "translated": text,
            "matched_phrases": [],
        }


def build_incident_summary(
    threat_type: Optional[str],
    severity: Optional[str],
    confidence: float,
    matched_keywords: Optional[List[str]] = None,
) -> str:
    """Build a short incident-summary block for the assistant response."""
    lines = ["### Incident Summary", ""]
    lines.append(f"**Category:** {threat_type or 'No specific threat detected'}")
    if severity:
        lines.append(f"**Severity:** {severity}")
    if confidence:
        lines.append(f"**Confidence:** {confidence:.0f}%")
    if matched_keywords:
        lines.append(f"**Signals:** {', '.join(matched_keywords)}")
    return "\n".join(lines)


def build_intent_explanation(
    intent: Optional[str],
    intent_confidence: float,
    matched_terms: Optional[List[str]] = None,
    question: bool = False,
) -> str:
    """Explain why the detector classified the message the way it did."""
    lines = ["### Detected Intent", ""]
    lines.append(f"**Intent:** {intent or 'Unknown'}")
    if intent_confidence:
        lines.append(f"**Confidence:** {intent_confidence:.0f}%")

    reasons: List[str] = []
    if matched_terms:
        reasons.append("Matched terms: " + ", ".join(matched_terms))
    if question:
        reasons.append("The message was phrased as a question rather than an active incident report.")
    if not reasons:
        reasons.append("The message did not contain enough incident-specific signals to classify it strongly.")

    lines.append("**Why:** " + " ".join(reasons))
    return "\n".join(lines)


def build_canonical_interpretation(
    question: str,
    translated_question: str,
    matched_phrases: Optional[List[str]] = None,
) -> str:
    """Show the normalized interpretation of the user's input."""
    lines = ["### Canonical Interpretation", ""]
    lines.append(f"**User input:** {question}")
    lines.append(f"**Canonical meaning:** {translated_question or question}")
    if matched_phrases:
        lines.append(f"**Matched phrases:** {', '.join(matched_phrases)}")
    return "\n".join(lines)


def translate_for_user(text: str, detected_language: str) -> str:
    """Translate display text into the user's detected language when possible."""
    if not text or detected_language in {"unknown", "english", ""}:
        return text

    translator_instance = get_app_translator()
    if translator_instance is None:
        return text

    try:
        return translator_instance.translate_to_language(text, detected_language)
    except Exception:
        logger.exception("Failed to translate assistant text for the detected language.")
        return text


USER_AVATAR = "🧑🏾"
ASSISTANT_AVATAR = "🛡️"

QUICK_PROMPTS = (
    "I think my WhatsApp was hacked",
    "Someone is asking for my BVN and OTP — is this a scam?",
    "What is phishing and how do I spot it?",
)

WELCOME_TIPS = (
    "Describe what happened in plain language and include any suspicious links or messages.",
    "Mention whether money, passwords, OTPs, or personal IDs were requested.",
    "The assistant can help assess risk and outline next steps, but always verify with official support channels.",
)

DO_NOT_SHARE_ITEMS = (
    "❌ Passwords", "❌ OTP Codes", "❌ BVN", "❌ NIN",
    "❌ ATM PIN", "❌ Bank Details",
)

# Mirrors .streamlit/config.toml — kept as plain hex here so custom HTML
# components (the verdict chip, hero banner) render correctly regardless
# of how Streamlit exposes theme colors as CSS variables internally.
#
# Tertiary color system (each is a primary+secondary mix, which reads as
# more sophisticated than a raw primary/secondary palette):
#   Indigo (blue-violet)   -> brand / primary accent
#   Magenta (red-violet)   -> scam alerts specifically
#   Teal (blue-green)      -> Low severity / safe
#   Olive (yellow-green)   -> Medium severity
#   Amber (yellow-orange)  -> High severity
#   Vermilion (red-orange) -> Critical severity
PALETTE = {
    "ink": "#0F1117",
    "panel": "#171A24",
    "panel_light": "#1E2230",
    "border": "#2A2E3A",
    "indigo": "#5B5FC7",
    "indigo_light": "#7A7EDB",
    "magenta": "#A83A7A",
    "magenta_bg": "#241323",
    "magenta_text": "#E8A8CF",
    "teal": "#2FA893",
    "teal_bg": "#12241F",
    "teal_text": "#8FE0D2",
    "olive": "#9AA83A",
    "olive_bg": "#20220F",
    "olive_text": "#D6DE9E",
    "amber": "#D69A3A",
    "amber_bg": "#26200F",
    "amber_text": "#F0CC8F",
    "vermilion": "#D6553A",
    "vermilion_bg": "#271410",
    "vermilion_text": "#F0A692",
    "bone": "#E7E6EA",
    "muted": "#8B8FA3",
}

# Severity label -> chip color set, keyed on the plain-text word inside
# Severity.value (e.g. "🔴 Critical" -> "Critical"). Forms a cool-to-hot
# gradient across four tertiary hues: Teal -> Olive -> Amber -> Vermilion.
_SEVERITY_STYLES = {
    "Critical": (PALETTE["vermilion_bg"], PALETTE["vermilion"], PALETTE["vermilion_text"], "●"),
    "High": (PALETTE["amber_bg"], PALETTE["amber"], PALETTE["amber_text"], "●"),
    "Medium": (PALETTE["olive_bg"], PALETTE["olive"], PALETTE["olive_text"], "●"),
    "Low": (PALETTE["teal_bg"], PALETTE["teal"], PALETTE["teal_text"], "●"),
}


# ==============================================================================
# ENGINE IMPORTS — graceful degradation
# ==============================================================================
# Each core engine is imported independently so that a missing or broken
# module disables only that one capability instead of crashing the whole
# app. The sidebar status indicators later reflect these flags directly,
# instead of hardcoded "Ready" messages that could lie about system health.
# ==============================================================================

try:
    from retriever import search_documents
    RETRIEVER_OK = True
except Exception:
    logger.exception("Retriever module failed to load; RAG context will be unavailable.")
    RETRIEVER_OK = False

    def search_documents(query: str) -> List[str]:
        return []

try:
    from generate_answer import generate_answer
    LLAMA_OK = True
except Exception:
    logger.exception("Answer-generation module failed to load; using fallback responses.")
    LLAMA_OK = False

    def generate_answer(question: str, context: str) -> str:
        return (
            "I'm currently unable to reach the offline AI response engine. "
            "Your report has still been analyzed and logged above if a "
            "threat or scam was detected — please try again shortly for "
            "a full written response."
        )

try:
    from threat_detector import analyze_threat
    THREAT_ENGINE_OK = True
except Exception:
    logger.exception("Threat detector failed to load; threat analysis is disabled.")
    THREAT_ENGINE_OK = False
    analyze_threat = None  # type: ignore[assignment]

try:
    from incident_response import get_incident_response
    INCIDENT_RESPONSE_OK = True
except Exception:
    logger.exception("Incident response module failed to load.")
    INCIDENT_RESPONSE_OK = False

    def get_incident_response(threat_type: str) -> List[str]:
        return []

try:
    from incident_logger import save_incident
    INCIDENT_LOGGER_OK = True
except Exception:
    logger.exception("Incident logger failed to load; incidents will not be persisted.")
    INCIDENT_LOGGER_OK = False

    def save_incident(*args: Any, **kwargs: Any) -> None:
        return None

try:
    from scam_detector import detect_scam
    SCAM_ENGINE_OK = True
except Exception:
    logger.exception("Scam detector failed to load; scam alerts are disabled.")
    SCAM_ENGINE_OK = False

    def detect_scam(text: str):
        return None


# ==============================================================================
# PAGE SETUP
# ==============================================================================

def configure_page() -> None:
    st.set_page_config(
        page_title="AfriShield AI",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(
        textwrap.dedent(f"""
        <style>
        #MainMenu {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}
        header {{ visibility: hidden; }}

        /* Tighten the default top padding now that the native header is hidden */
        .block-container {{ padding-top: 2rem; max-width: 900px; }}

        /* --- Sidebar brand lockup --- */
        [data-testid="stSidebar"] {{
            border-right: 1px solid {PALETTE["border"]};
        }}
        .afs-brand {{
            display: flex;
            align-items: center;
            gap: 0.6rem;
            padding-bottom: 0.25rem;
        }}
        .afs-brand-icon {{
            font-size: 1.9rem;
            line-height: 1;
        }}
        .afs-brand-text h1 {{
            font-family: "Space Grotesk", sans-serif;
            font-size: 1.25rem;
            font-weight: 700;
            margin: 0;
            letter-spacing: 0.01em;
            color: {PALETTE["bone"]};
        }}
        .afs-brand-text p {{
            font-family: "IBM Plex Mono", monospace;
            font-size: 0.72rem;
            color: {PALETTE["muted"]};
            margin: 0;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }}

        /* --- Engine status console rows --- */
        .afs-status-row {{
            display: flex;
            align-items: center;
            gap: 0.55rem;
            padding: 0.3rem 0;
            font-family: "IBM Plex Mono", monospace;
            font-size: 0.82rem;
            color: {PALETTE["bone"]};
        }}
        .afs-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            flex-shrink: 0;
        }}

        /* --- Hero banner on the main page --- */
        .afs-hero {{
            border: 1px solid {PALETTE["border"]};
            border-radius: 10px;
            background: linear-gradient(135deg, {PALETTE["panel"]} 0%, {PALETTE["ink"]} 100%);
            padding: 1.4rem 1.6rem;
            margin-bottom: 1.4rem;
            position: relative;
            overflow: hidden;
        }}
        .afs-hero::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: linear-gradient(90deg, {PALETTE["indigo"]} 0%, {PALETTE["magenta"]} 100%);
        }}
        .afs-hero-title {{
            font-family: "Space Grotesk", sans-serif;
            font-size: 1.9rem;
            font-weight: 700;
            color: {PALETTE["bone"]};
            margin: 0 0 0.3rem 0;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .afs-hero-tagline {{
            font-family: "IBM Plex Mono", monospace;
            font-size: 0.85rem;
            color: {PALETTE["muted"]};
            margin: 0;
        }}

        /* --- Verdict chip (the recurring "AI verdict" signature element) --- */
        .afs-verdict {{
            border: 1px solid var(--afs-verdict-border, {PALETTE["border"]});
            background: var(--afs-verdict-bg, {PALETTE["panel"]});
            border-radius: 8px;
            padding: 0.75rem 1rem;
            margin-bottom: 0.6rem;
        }}
        .afs-verdict-row {{
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 0.4rem;
        }}
        .afs-verdict-category {{
            font-family: "Space Grotesk", sans-serif;
            font-weight: 600;
            font-size: 1.02rem;
            color: {PALETTE["bone"]};
        }}
        .afs-verdict-meta {{
            font-family: "IBM Plex Mono", monospace;
            font-size: 0.82rem;
            color: var(--afs-verdict-text, {PALETTE["muted"]});
        }}

        /* --- Chat bubbles --- */
        [data-testid="stChatMessage"] {{
            border: 1px solid {PALETTE["border"]};
            border-radius: 10px;
            padding: 0.4rem 0.2rem;
        }}

        /* --- Welcome / empty state --- */
        .afs-welcome {{
            padding: 0.4rem 0.1rem 0.9rem 0.1rem;
        }}
        .afs-welcome-title {{
            font-family: "Space Grotesk", sans-serif;
            font-size: 1.05rem;
            font-weight: 600;
            color: {PALETTE["bone"]};
            margin: 0 0 0.15rem 0;
        }}
        .afs-welcome-sub {{
            font-family: "IBM Plex Mono", monospace;
            font-size: 0.78rem;
            color: {PALETTE["muted"]};
            margin: 0 0 0.7rem 0;
        }}

        /* --- Footer disclaimer --- */
        .afs-footer {{
            font-family: "IBM Plex Mono", monospace;
            font-size: 0.72rem;
            color: {PALETTE["muted"]};
            text-align: center;
            padding-top: 1rem;
        }}
        </style>
        """).strip(),
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    st.markdown(
        textwrap.dedent(f"""
        <div class="afs-hero">
            <p class="afs-hero-title">🛡️ AfriShield AI Cybersecurity Assistant</p>
            <p class="afs-hero-tagline">{APP_TAGLINE}</p>
        </div>
        """).strip(),
        unsafe_allow_html=True,
    )


def render_welcome() -> None:
    st.markdown(
        textwrap.dedent("""
        <div class="afs-welcome">
            <p class="afs-welcome-title">👋 Start by describing a security concern</p>
            <p class="afs-welcome-sub">Or try one of these</p>
        </div>
        """).strip(),
        unsafe_allow_html=True,
    )
    cols = st.columns(len(QUICK_PROMPTS))
    for col, prompt in zip(cols, QUICK_PROMPTS):
        with col:
            if st.button(prompt, use_container_width=True, key=f"quick_{prompt}"):
                st.session_state["_pending_question"] = prompt
                st.rerun()

    with st.expander("💡 Quick guidance", expanded=False):
        for tip in WELCOME_TIPS:
            st.write(f"• {tip}")


def render_verdict_chip(category: str, severity_value: str, confidence: float) -> None:
    """The one consistent, recurring visual element for every threat
    verdict — same style in chat history and in a freshly generated
    response, styled by severity."""
    severity_word = severity_value.split(" ", 1)[-1] if severity_value else "Low"
    bg, border, text_color, dot = _SEVERITY_STYLES.get(
        severity_word, _SEVERITY_STYLES["Low"]
    )
    st.markdown(
        textwrap.dedent(f"""
        <div class="afs-verdict" style="--afs-verdict-bg:{bg}; --afs-verdict-border:{border}; --afs-verdict-text:{text_color};">
            <div class="afs-verdict-row">
                <span class="afs-verdict-category"><span style="color:{border};">{dot}</span> {category}</span>
                <span class="afs-verdict-meta">{severity_word.upper()} · {confidence:.0f}% confidence</span>
            </div>
        </div>
        """).strip(),
        unsafe_allow_html=True,
    )


def render_scam_banner(scam_type: str) -> None:
    """Scam alerts get their own magenta (red-violet) treatment, distinct
    from the teal/olive/amber/vermilion threat-severity gradient — a scam
    report is a different kind of alert from a technical incident, and
    the color makes that immediately legible at a glance."""
    st.markdown(
        textwrap.dedent(f"""
        <div class="afs-verdict" style="--afs-verdict-bg:{PALETTE['magenta_bg']}; --afs-verdict-border:{PALETTE['magenta']}; --afs-verdict-text:{PALETTE['magenta_text']};">
            <div class="afs-verdict-row">
                <span class="afs-verdict-category"><span style="color:{PALETTE['magenta']};">●</span> Scam Alert: {scam_type}</span>
                <span class="afs-verdict-meta">SOCIAL ENGINEERING</span>
            </div>
        </div>
        """).strip(),
        unsafe_allow_html=True,
    )


def init_session_state() -> None:
    st.session_state.setdefault("messages", [])


# ==============================================================================
# HELPERS
# ==============================================================================

def load_incident_count(path: str = INCIDENT_LOG_PATH) -> int:
    """Number of logged incidents. Defaults to 0 on any missing file,
    unreadable JSON, or IO error — never raises."""
    if not os.path.exists(path):
        return 0
    try:
        with open(path, "r", encoding="utf-8") as f:
            logs = json.load(f)
        return len(logs) if isinstance(logs, list) else 0
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Could not read incident log at %s: %s", path, exc)
        return 0


def _engine_status(label: str, ok: bool) -> None:
    color = PALETTE["teal"] if ok else PALETTE["vermilion"]
    state = "Ready" if ok else "Unavailable"
    st.markdown(
        textwrap.dedent(f"""
        <div class="afs-status-row">
            <span class="afs-dot" style="background:{color};"></span>
            <span>{label} — {state}</span>
        </div>
        """).strip(),
        unsafe_allow_html=True,
    )


# ==============================================================================
# SIDEBAR
# ==============================================================================

def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            textwrap.dedent("""
            <div class="afs-brand">
                <div class="afs-brand-icon">🛡️</div>
                <div class="afs-brand-text">
                    <h1>AfriShield AI</h1>
                    <p>Cybersecurity Intelligence</p>
                </div>
            </div>
            """).strip(),
            unsafe_allow_html=True,
        )
        st.divider()

        st.metric("🚨 Incidents Logged", load_incident_count())
        st.divider()

        st.caption("ENGINE STATUS")
        _engine_status("Translation / Language Layer", TRANSLATION_OK)
        _engine_status("Threat Engine", THREAT_ENGINE_OK)
        _engine_status("Scam Engine", SCAM_ENGINE_OK)
        _engine_status("RAG Knowledge Base", RETRIEVER_OK)
        _engine_status("LLM Response Generator", LLAMA_OK)
        st.divider()

        st.subheader("📊 Session Statistics")
        messages = st.session_state.messages
        st.metric("Messages", len(messages))
        threats_detected = sum(1 for m in messages if m.get("threat"))
        st.metric("Threats Detected", threats_detected)
        st.divider()

        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        if messages:
            st.download_button(
                label="⬇️ Export Chat",
                data=json.dumps(messages, indent=2),
                file_name=f"afrishield_chat_{datetime.now():%Y%m%d_%H%M%S}.json",
                mime="application/json",
                use_container_width=True,
            )

        st.divider()
        st.caption(f"AfriShield AI v{APP_VERSION}")
        st.caption(CHALLENGE_TAG)


 # ==============================================================================
# CHAT RENDERING (single source of truth for both history + live messages)
# ==============================================================================

def render_assistant_message(msg: Dict[str, Any]) -> None:
    threat_label = msg.get("threat_display") or msg.get("threat")

    if msg.get("threat"):
        confidence = msg.get("confidence") or 0
        render_verdict_chip(
            threat_label,
            msg.get("severity") or "",
            confidence
        )
        st.progress(min(int(confidence), 100))

    scam_label = msg.get("scam_display") or msg.get("scam")

    if msg.get("scam"):
        render_scam_banner(scam_label)

    # --------------------------------------------------------------------------
    # Canonical interpretation
    # --------------------------------------------------------------------------
    canonical = msg.get("canonical_interpretation")

    if canonical:
        st.info(canonical)

    # --------------------------------------------------------------------------
    # Incident / intent information
    # --------------------------------------------------------------------------
    if msg.get("incident_summary"):
        st.markdown(msg["incident_summary"])

    if msg.get("intent_explanation"):
        st.markdown(msg["intent_explanation"])

    # --------------------------------------------------------------------------
    # Explainability
    # --------------------------------------------------------------------------
    if msg.get("explainability"):
        with st.expander("🔎 Why this was classified this way"):
            st.markdown(msg["explainability"])

    # --------------------------------------------------------------------------
    # Main AI response
    # --------------------------------------------------------------------------
    content = msg.get("content") or ""

    # If canonical interpretation has accidentally been included
    # inside the main content, don't render it a second time.
    if canonical and content.strip() == canonical.strip():
        content = ""

    if content:
        st.markdown(content)

    # --------------------------------------------------------------------------
    # Recommendations
    # --------------------------------------------------------------------------
    recommendations = (
        msg.get("recommendations_display")
        or msg.get("recommendations")
        or []
    )

    if recommendations:
        st.subheader("🛠 Recommended Actions")

        for item in recommendations:
            st.success(item)

    # --------------------------------------------------------------------------
    # Threat analysis details
    # --------------------------------------------------------------------------
    if msg.get("threat"):
        with st.expander("🔍 Threat Analysis Details"):
            st.write("Intent:", msg.get("intent") or "—")
            st.write(
                "Matched Signals:",
                msg.get("matched_keywords") or []
            )

            if msg.get("matched_phrases"):
                st.write(
                    "Matched Translation Phrases:",
                    msg.get("matched_phrases")
                )


def render_chat_history() -> None:
    for msg in st.session_state.messages:
        avatar = (
            ASSISTANT_AVATAR
            if msg["role"] == "assistant"
            else USER_AVATAR
        )

        with st.chat_message(msg["role"], avatar=avatar):
            if msg["role"] == "assistant":
                render_assistant_message(msg)
            else:
                st.write(msg["content"])    


# ==============================================================================
# CORE PIPELINE: scam detection -> threat analysis -> RAG -> generation
# ==============================================================================

def analyze_user_message(question: str) -> Dict[str, Any]:
    """Run the full detection + RAG + generation pipeline for one user
    message and return an assistant message dict ready to store/render.
    Every external engine call is isolated so one failure degrades that
    feature only, instead of crashing the whole response."""

    # Translate user text into canonical English and detect language.
    translation_details = safe_translate_message(question)

    detected_language = translation_details.get("language", "unknown") or "unknown"
    translated_question = translation_details.get("translated", question)
    matched_phrases: list[str] = translation_details.get("matched_phrases", [])

    scam_result = None
    if SCAM_ENGINE_OK:
        try:
            scam_result = detect_scam(translated_question)
        except Exception:
            logger.exception("Scam detection failed for this message.")

    threat_type = severity = intent = None
    confidence = 0.0
    matched_keywords: list[str] = []
    recommendations: list[str] = []
    intent_confidence = 0.0
    incident_type = None

    analysis = None
    if THREAT_ENGINE_OK:
        try:
            analysis = analyze_threat(translated_question)
        except Exception:
            logger.exception("Threat analysis failed for this message.")

    if analysis is not None and analysis.category != "General Security Question":
        threat_type = analysis.category
        severity = analysis.severity.value
        confidence = analysis.confidence
        incident_type = analysis.incident_type.value
        intent = analysis.user_intent.value
        intent_confidence = analysis.intent_confidence
        matched_keywords = analysis.matched_keywords

        if INCIDENT_RESPONSE_OK:
            try:
                recommendations = get_incident_response(threat_type)
            except Exception:
                logger.exception("Failed to fetch incident response actions.")

        if INCIDENT_LOGGER_OK:
            try:
                save_incident(translated_question, threat_type, severity, confidence)
            except Exception:
                logger.exception("Failed to persist incident log.")

    try:
        documents = search_documents(translated_question) if RETRIEVER_OK else []
    except Exception:
        logger.exception("Document retrieval failed.")
        documents = []

    context = "\n\n".join(documents)
    if threat_type:
        context += (
            f"\n\nThreat Analysis:\nCategory: {threat_type}\n"
            f"Severity: {severity}\nConfidence: {confidence:.0f}%\n\n"
            f"Recommended Response:\n{recommendations}"
        )

    try:
        answer = generate_answer(translated_question, context)
    except Exception:
        logger.exception("Answer generation failed.")
        answer = (
            "I'm having trouble generating a full response right now. "
            "Your report has still been analyzed and logged above if a "
            "threat or scam was detected — please try again shortly."
        )

    canonical_interpretation = build_canonical_interpretation(question, translated_question, matched_phrases)
    incident_summary = build_incident_summary(threat_type, severity, confidence, matched_keywords) if threat_type else None
    intent_explanation = build_intent_explanation(
        intent,
        intent_confidence,
        matched_keywords or None,
        question=translated_question.endswith("?"),
    ) if intent else None
    explainability = None
    if matched_keywords:
        explainability = "\n".join(
            [
                "**Why this was flagged:**",
                f"- Matched signals: {', '.join(matched_keywords)}",
                f"- Confidence: {confidence:.0f}%",
                f"- Incident type: {incident_type or 'Unknown'}",
            ]
        )

    response_sections: list[str] = []
    # Canonical interpretation is rendered separately by
    # render_assistant_message(), so do not add it to response_sections.
    if incident_summary:
        response_sections.append(incident_summary)
    if intent_explanation:
        response_sections.append(intent_explanation)
    if scam_result:
        do_not_share = "\n".join(f"- {item}" for item in DO_NOT_SHARE_ITEMS)
        scam_block = (
            f"### Scam Alert\n\n"
            f"**Scam Type:** {scam_result}\n\n"
            f"**Never share:**\n{do_not_share}"
        )
        response_sections.append(scam_block)
    response_sections.append(answer)

    final_answer = "\n\n".join(section for section in response_sections if section)
    translated_recommendations = recommendations
    translated_threat_type = threat_type
    translated_scam_result = scam_result

    if detected_language not in {"unknown", "english"}:
        translator_instance = get_app_translator()
        if translator_instance is not None:
            try:
                final_answer = translate_for_user(final_answer, detected_language)
                translated_recommendations = [
                    translator_instance.translate_to_language(item, detected_language)
                    for item in recommendations
                ] if recommendations else []
                translated_threat_type = (
                    translator_instance.translate_to_language(threat_type, detected_language)
                    if threat_type else None
                )
                translated_scam_result = (
                    translator_instance.translate_to_language(scam_result, detected_language)
                    if scam_result else None
                )
            except Exception:
                logger.exception("Response translation failed.")

    return {
        "role": "assistant",
        "content": final_answer,
        "threat": threat_type,
        "threat_display": translated_threat_type,
        "severity": severity,
        "confidence": confidence,
        "recommendations": recommendations,
        "recommendations_display": translated_recommendations,
        "scam": translated_scam_result,
        "scam_display": translated_scam_result,
        "intent": intent,
        "incident_summary": incident_summary,
        "intent_explanation": intent_explanation,
        "canonical_interpretation": canonical_interpretation,
        "explainability": explainability,
        "matched_keywords": matched_keywords,
        "matched_phrases": matched_phrases,
    }


# ==============================================================================
# MAIN
# ==============================================================================

def main() -> None:
    configure_page()
    init_session_state()
    render_sidebar()

    render_hero()

    render_chat_history()

    if not st.session_state.messages:
        render_welcome()

    pending_question = st.session_state.pop("_pending_question", None)
    typed_question = st.chat_input("Describe a cyber incident or ask a security question...")
    question = pending_question or typed_question

    if not question or not question.strip():
        st.markdown(
            '<p class="afs-footer">AfriShield AI gives general security guidance — '
            "always verify independently and contact your bank or provider directly "
            "for account-specific action.</p>",
            unsafe_allow_html=True,
        )
        return

    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.write(question)

    with st.spinner("🛡️ AfriShield AI analyzing..."):
        assistant_message = analyze_user_message(question)

    st.session_state.messages.append(assistant_message)

    with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
        render_assistant_message(assistant_message)


if __name__ == "__main__":
    main()

 