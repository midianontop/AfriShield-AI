"""
================================================================================
  AFRISHIELD AI  —  African AI Security Assistant
  Cyber Threat Detection Engine
================================================================================

  Classifies user-reported security incidents (hacked accounts, malware,
  ransomware, data breaches, DDoS, fraud, phishing) and returns a severity
  rating, confidence score, and clear next-step guidance.

  v3.0 additions:
    • Fuzzy matching + lightweight stemming (typo / morphology tolerant)
    • Intent detection — separates a genuine "Active Incident" report
      from a general "Security Question" so questions aren't over-scored
    • Expanded African cyber-fraud vocabulary (Nigeria, Kenya, South Africa)
    • A pluggable Retrieval-Augmented-Generation (RAG) layer: a local
      knowledge base (NIST / OWASP / CERT references) feeds a response
      generator, whose interface is designed to be backed by a real LLM
      (e.g. Llama 3.2) in production — see `ThreatResponseGenerator`.

  v3.1 tuning:
    • Fuzzy threshold raised 0.84 → 0.90 (stricter typo tolerance)
    • Phrase slack reduced 2 → 1 (tighter word-order flexibility)
    • Stemmer no longer strips bare "s" plurals (was over-merging words)
    • Confidence curve flattened: 45+12x → 35+10x
    • Security-question confidence now scaled ×0.35 (was unchanged)
    • Severity escalation loosened: 90%+3 signals → 85%+2 signals
    • RAG retrieval now returns top_k=3 references (was 2)
    • Reweighted keywords: hacked 2→1, unauthorized access 3→4, scam 1→2

  Author  : Midian
  Module  : threat_detector.py
  Version : 3.1.0
================================================================================
"""

from __future__ import annotations

import difflib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


# ==============================================================================
# SEVERITY LEVELS
# ==============================================================================

class Severity(Enum):
    LOW = "🟢 Low"
    MEDIUM = "🟡 Medium"
    HIGH = "🟠 High"
    CRITICAL = "🔴 Critical"

    @property
    def rank(self) -> int:
        return {"🟢 Low": 0, "🟡 Medium": 1, "🟠 High": 2, "🔴 Critical": 3}[self.value]

    @classmethod
    def from_rank(cls, rank: int) -> "Severity":
        rank = max(0, min(rank, 3))
        return [cls.LOW, cls.MEDIUM, cls.HIGH, cls.CRITICAL][rank]


# ==============================================================================
# INTENT / ATTACK-INTENT DETECTION
# ==============================================================================
# Not every message that mentions "ransomware" is an active incident — some
# are just people asking what ransomware IS. We classify intent separately
# so a curious question doesn't get treated (or scored) like a live attack.
# ==============================================================================

class IncidentType(Enum):
    ACTIVE_INCIDENT = "🚨 Active Incident"
    SECURITY_QUESTION = "❓ Security Question"


_QUESTION_WORDS = {
    "what", "how", "why", "when", "who", "which", "can", "could",
    "does", "do", "is", "are", "should", "would", "explain", "define",
}

_INCIDENT_MARKERS = (
    "my ", "our ", "i've", "i have", "i'm", "i am", "we're", "we are",
    "currently", "right now", "just happened", "just now", "someone",
    "they stole", "they hacked", "help me", "please help", "urgent",
)


def _detect_intent(text: str) -> IncidentType:
    """
    Heuristically classify whether a message is reporting a live incident
    ("my account was hacked") vs. asking a general security question
    ("what is phishing?"). First-person / experiential language always
    wins, since "My account was hacked, what do I do?" is still a real
    incident even though it contains a question mark.
    """
    t = text.strip().lower()
    if not t:
        return IncidentType.SECURITY_QUESTION

    if any(marker in t for marker in _INCIDENT_MARKERS):
        return IncidentType.ACTIVE_INCIDENT

    first_word = t.split()[0].strip("?.,!") if t.split() else ""
    if t.endswith("?") or first_word in _QUESTION_WORDS:
        return IncidentType.SECURITY_QUESTION

    return IncidentType.ACTIVE_INCIDENT


# ==============================================================================
# FUZZY MATCHING + LIGHTWEIGHT STEMMING
# ==============================================================================
# Replaces rigid exact-substring keyword matching with tolerance for typos
# ("ransomwear"), morphology ("encrypted" / "encrypting" / "encrypts"), and
# minor phrasing drift — without pulling in an external NLP dependency.
# ==============================================================================

_SUFFIXES = ("ingly", "edly", "ing", "edness", "ed", "es")


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", text.lower())


def _stem(word: str) -> str:
    """Crude suffix-stripping stemmer — good enough to unify word forms
    like hack/hacked/hacking or leak/leaked/leaks without a dependency."""
    for suf in _SUFFIXES:
        if word.endswith(suf) and len(word) - len(suf) >= 3:
            return word[: -len(suf)]
    return word


def _tokens_match(a: str, b: str, threshold: float = 0.90) -> bool:
    """True if two tokens are identical, share a stem, or are close enough
    (typo-level) per difflib's similarity ratio."""
    if a == b:
        return True
    if _stem(a) == _stem(b):
        return True
    if abs(len(a) - len(b)) <= 2:
        return difflib.SequenceMatcher(None, a, b).ratio() >= threshold
    return False


def _phrase_matches(tokens: list[str], keyword: str, slack: int = 1) -> bool:
    """
    Fuzzy, order-independent match of a (possibly multi-word) keyword
    against a token stream. Uses a sliding window slightly larger than
    the keyword itself (`slack` extra tokens) so filler words and
    reordering ("files are encrypted" vs. "encrypted files") still
    count as a match, while fuzzy/stemmed comparison absorbs typos
    and morphological variants at the individual-word level.
    """
    kw_tokens = _tokenize(keyword)
    n = len(kw_tokens)
    if n == 0 or n > len(tokens):
        return False

    window_size = n + slack
    for start in range(len(tokens)):
        window = tokens[start:start + window_size]
        if len(window) < n:
            break
        remaining = list(window)
        matched_all = True
        for kw in kw_tokens:
            found_idx = next(
                (idx for idx, w in enumerate(remaining) if _tokens_match(w, kw)),
                None,
            )
            if found_idx is None:
                matched_all = False
                break
            remaining.pop(found_idx)
        if matched_all:
            return True
    return False


# ==============================================================================
# THREAT CATEGORY DEFINITIONS
# ==============================================================================
# Each category carries:
#   - keywords     : phrase -> weight (higher = stronger signal)
#   - base_severity: the category's default severity
#   - remediation  : immediate, practical response steps
#
# Includes African cyber-fraud vocabulary:
#   🇳🇬 Nigeria      : OPay, PalmPay, BVN, NIN, WhatsApp takeover, SIM swap, 419
#   🇰🇪 Kenya        : M-Pesa fraud
#   🇿🇦 South Africa : EFT fraud
# ==============================================================================

THREAT_CATEGORIES: dict[str, dict] = {
    "Ransomware Attack": {
        "keywords": {
            "ransomware": 4, "encrypted files": 3, "pay bitcoin": 3,
            "pay ransom": 4, "locked files": 3, "decrypt files": 3,
            "files held hostage": 3, "ransom note": 3,
        },
        "base_severity": Severity.CRITICAL,
        "remediation": (
            "Disconnect the affected device from the network immediately. "
            "Do NOT pay the ransom. Report to your IT/security team or "
            "national CERT, and restore from a clean backup if available."
        ),
    },
    "Account/Device Compromise": {
        "keywords": {
            "hacked": 1, "hack": 1, "compromised": 2, "breached": 2,
            "unauthorized access": 4, "someone logged in": 2,
            "account stolen": 3, "phone hacked": 3, "facebook hacked": 2,
            "gmail hacked": 2, "instagram hacked": 2, "whatsapp hacked": 2,
            "whatsapp takeover": 3, "sim swap": 3, "sim swapped": 3,
            "cloned my number": 3,
        },
        "base_severity": Severity.HIGH,
        "remediation": (
            "Change your password immediately from a trusted device, "
            "enable two-factor authentication, log out of all sessions, "
            "and contact your service provider if your SIM was affected."
        ),
    },
    "Malware Infection": {
        "keywords": {
            "malware": 3, "virus": 2, "trojan": 3, "spyware": 3,
            "worm": 2, "keylogger": 3, "infected device": 3,
            "malicious software": 3, "phone acting strange": 1,
            "pop up ads everywhere": 1, "apps installing themselves": 2,
        },
        "base_severity": Severity.HIGH,
        "remediation": (
            "Disconnect from the internet, run a full scan with trusted "
            "antivirus software, and avoid entering passwords until the "
            "device is confirmed clean. Consider a factory reset if severe."
        ),
    },
    "Phishing Attack": {
        "keywords": {
            "phishing": 3, "fake email": 2, "fake website": 2,
            "suspicious link": 2, "verify account": 2, "login link": 2,
            "credential theft": 3, "password stolen": 3,
            "fake bank sms": 2, "clone website": 2,
        },
        "base_severity": Severity.HIGH,
        "remediation": (
            "Do not click any links or enter credentials. Verify requests "
            "directly with the organization through official channels, "
            "and change any passwords you may have already entered."
        ),
    },
    "Financial Fraud": {
        "keywords": {
            "scam": 2, "fraud": 1, "otp": 2, "bank details": 2,
            "atm card": 2, "bvn": 2, "nin": 2, "financial loss": 2,
            "money stolen": 3, "unauthorized transaction": 3,
            "mobile money fraud": 3, "momo stolen": 2,
            # Nigeria
            "opay": 2, "palmpay": 2, "419 scam": 3, "advance fee fraud": 3,
            # Kenya
            "m-pesa": 2, "mpesa": 2, "m-pesa fraud": 3,
            # South Africa
            "eft fraud": 3, "electronic funds transfer fraud": 3,
        },
        "base_severity": Severity.MEDIUM,
        "remediation": (
            "Contact your bank or mobile money provider immediately to "
            "freeze the account, never share your OTP, BVN, NIN, or PIN, "
            "and file a report with your local financial fraud/cybercrime unit."
        ),
    },
    "Data Breach": {
        "keywords": {
            "data leak": 3, "data breach": 3, "customer data exposed": 3,
            "database leaked": 3, "sensitive information exposed": 3,
            "records leaked": 2, "personal data exposed": 3,
        },
        "base_severity": Severity.HIGH,
        "remediation": (
            "Identify the scope of exposed data, notify affected users, "
            "rotate any exposed credentials/API keys, and report the "
            "incident to the relevant data protection authority."
        ),
    },
    "DDoS Attack": {
        "keywords": {
            "ddos": 3, "denial of service": 3, "website down": 1,
            "traffic attack": 2, "service unavailable": 1,
            "server overloaded": 2, "flooded with requests": 3,
        },
        "base_severity": Severity.HIGH,
        "remediation": (
            "Enable DDoS protection/mitigation through your hosting or "
            "CDN provider, monitor traffic sources, and notify your "
            "network/security team to filter malicious traffic."
        ),
    },
}


# ==============================================================================
# RAG LAYER — knowledge base (retrieval) + response generator (generation)
# ==============================================================================
# This mirrors a real RAG pipeline's shape:
#     user report -> detector -> retriever (docs) -> generator (LLM) -> answer
#
# `ThreatKnowledgeBase` stands in for a vector store: in production, swap it
# for embeddings over the full NIST / OWASP / CERT corpora. `TemplateResponse
# Generator` stands in for the LLM call: swap it for a real Llama 3.2 (local
# inference) or hosted model by subclassing `ThreatResponseGenerator` and
# overriding `generate()` — the rest of the pipeline is already wired for it.
# ==============================================================================

class ThreatKnowledgeBase:
    """Lightweight, fully-offline stand-in for a RAG retriever."""

    _REFERENCES: dict[str, list[str]] = {
        "Ransomware Attack": [
            "NIST SP 1800-11 (Ransomware Recovery) — isolate the host, do not pay, restore from clean backup.",
            "CISA/CERT Ransomware Guide — preserve evidence and log timestamps before wiping any device.",
            "OWASP Ransomware Prevention Cheat Sheet — maintain offline, tested backups.",
        ],
        "Account/Device Compromise": [
            "OWASP Account Takeover Prevention Cheat Sheet — enforce MFA and rotate credentials.",
            "CERT Advisory — report SIM-swap fraud to your telecom provider immediately.",
            "NIST SP 800-63B (Digital Identity Guidelines) — credential recovery best practices.",
        ],
        "Malware Infection": [
            "NIST SP 800-83 (Malware Incident Prevention & Handling Guide).",
            "OWASP Mobile Security Guide — factory-reset if reinfection persists after cleanup.",
            "CERT Advisory — isolate infected devices from shared networks immediately.",
        ],
        "Phishing Attack": [
            "OWASP Phishing Guidance — verify sender domain before any credential entry.",
            "CERT Phishing Response Checklist — report and block the sending domain/number.",
            "NIST SP 800-177 (Trustworthy Email) — email authentication and verification practices.",
        ],
        "Financial Fraud": [
            "CBN/NIBSS Fraud Guidelines — freeze the account and file a cybercrime report.",
            "CERT Advisory — never share OTP, BVN, NIN, or mobile-money PINs with anyone.",
            "OWASP Fraud Prevention Cheat Sheet — verify transactions through a second channel.",
        ],
        "Data Breach": [
            "NIST SP 800-61 (Computer Security Incident Handling Guide).",
            "OWASP Breach Notification Guidance — notify affected users without undue delay.",
            "CERT Data Breach Checklist — rotate credentials and audit access logs.",
        ],
        "DDoS Attack": [
            "NIST SP 800-61 — traffic-filtering and containment steps for DDoS.",
            "CERT DDoS Quick Reference — engage your CDN/hosting provider's mitigation service.",
            "OWASP DDoS Prevention Cheat Sheet — rate-limit and monitor traffic patterns.",
        ],
    }

    def retrieve(self, category: str, top_k: int = 3) -> list[str]:
        return self._REFERENCES.get(category, [])[:top_k]


class ThreatResponseGenerator:
    """
    Base interface for the "generation" stage of the RAG pipeline.

    Swap this for a real LLM in production, e.g.:

        class LlamaResponseGenerator(ThreatResponseGenerator):
            def generate(self, text, category, severity, references, remediation):
                prompt = build_prompt(text, category, severity, references, remediation)
                return llama_client.complete(prompt)   # Llama 3.2, local or hosted

    The detector, knowledge base, and result object are already wired to
    accept whatever this returns — no other code needs to change.
    """

    def generate(
        self,
        text: str,
        category: str,
        severity: Severity,
        references: list[str],
        remediation: str,
    ) -> str:
        raise NotImplementedError


class TemplateResponseGenerator(ThreatResponseGenerator):
    """Default, fully-offline generator (no external model required)."""

    def generate(
        self,
        text: str,
        category: str,
        severity: Severity,
        references: list[str],
        remediation: str,
    ) -> str:
        ref_line = " ".join(f"[{r}]" for r in references) if references else ""
        message = (
            f"This looks like a {category} case ({severity.value} severity). "
            f"{remediation}"
        )
        return f"{message} {ref_line}".strip()


# ==============================================================================
# RESULT OBJECT
# ==============================================================================

@dataclass
class ThreatAnalysisResult:
    text: str
    category: str
    severity: Severity
    confidence: float
    incident_type: IncidentType = IncidentType.ACTIVE_INCIDENT
    matched_keywords: list[str] = field(default_factory=list)
    remediation: str = ""
    references: list[str] = field(default_factory=list)
    generated_response: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def summary(self) -> str:
        lines = [
            "=" * 60,
            "  AFRISHIELD AI — Threat Analysis Report",
            "=" * 60,
            f"Intent         : {self.incident_type.value}",
            f"Category       : {self.category}",
            f"Severity       : {self.severity.value}",
            f"Confidence     : {self.confidence:.0f}%",
        ]
        if self.matched_keywords:
            lines.append(f"Matched Signals: {', '.join(self.matched_keywords)}")
        if self.references:
            lines.append("References     :")
            for ref in self.references:
                lines.append(f"  • {ref}")
        if self.generated_response:
            lines.append(f"\nAfriShield AI Response:\n  {self.generated_response}")
        elif self.remediation:
            lines.append(f"\nRecommended Action:\n  {self.remediation}")
        lines.append("=" * 60)
        return "\n".join(lines)


# ==============================================================================
# CORE DETECTOR
# ==============================================================================

class ThreatDetector:
    """
    AfriShield AI's core cyber-threat classification engine.

    Scans free-text incident reports for known threat patterns (using
    fuzzy, typo-tolerant matching), separates genuine incidents from
    general security questions, and returns a severity rating, confidence
    score, retrieved reference material, and an AI-generated response.
    """

    def __init__(
        self,
        categories: dict[str, dict] | None = None,
        knowledge_base: ThreatKnowledgeBase | None = None,
        generator: ThreatResponseGenerator | None = None,
    ):
        self.categories = categories or THREAT_CATEGORIES
        self.knowledge_base = knowledge_base or ThreatKnowledgeBase()
        self.generator = generator or TemplateResponseGenerator()

    @staticmethod
    def _normalize(text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"\s+", " ", text)
        return text

    def _score_category(self, tokens: list[str], keywords: dict[str, int]) -> tuple[int, list[str]]:
        score = 0
        matches: list[str] = []
        for keyword, weight in keywords.items():
            if _phrase_matches(tokens, keyword):
                score += weight
                matches.append(keyword)
        return score, matches

    @staticmethod
    def _confidence_from_score(score: int) -> float:
        """Diminishing-returns confidence curve capped at ~98%."""
        if score <= 0:
            return 0.0
        return round(min(98.0, 35 + score * 10), 1)

    def analyze(self, text: str) -> ThreatAnalysisResult:
        """Analyze an incident report and return a full ThreatAnalysisResult."""
        if not text or not text.strip():
            return ThreatAnalysisResult(
                text=text,
                category="No Threat Detected",
                severity=Severity.LOW,
                confidence=0.0,
                incident_type=IncidentType.SECURITY_QUESTION,
            )

        intent = _detect_intent(text)
        normalized = self._normalize(text)
        tokens = _tokenize(normalized)

        best_category = None
        best_score = 0
        best_matches: list[str] = []

        for category, data in self.categories.items():
            score, matches = self._score_category(tokens, data["keywords"])
            if score > best_score:
                best_category = category
                best_score = score
                best_matches = matches

        if best_category is None:
            return ThreatAnalysisResult(
                text=text,
                category="General Security Question",
                severity=Severity.LOW,
                confidence=0.0,
                incident_type=IncidentType.SECURITY_QUESTION,
                remediation=(
                    "No specific threat indicators found. If you suspect "
                    "something is wrong, describe the exact symptoms "
                    "(unexpected messages, pop-ups, transactions, etc.) "
                    "for a more precise assessment."
                ),
            )

        category_data = self.categories[best_category]
        base_severity = category_data["base_severity"]
        confidence = self._confidence_from_score(best_score)

        # A general question that happens to mention threat vocabulary
        # ("What is ransomware?") is informational, not a live incident —
        # keep the topic for context but don't alarm-rate it as an attack.
        if intent == IncidentType.SECURITY_QUESTION:
            severity = Severity.LOW
            confidence = round(confidence * 0.35, 1)
        else:
            # Escalate severity by one level when multiple strong signals
            # corroborate the same category (high-confidence match).
            severity = base_severity
            if confidence >= 85 and len(best_matches) >= 2:
                severity = Severity.from_rank(base_severity.rank + 1)

        references = self.knowledge_base.retrieve(best_category)
        generated_response = self.generator.generate(
            text=text,
            category=best_category,
            severity=severity,
            references=references,
            remediation=category_data["remediation"],
        )

        return ThreatAnalysisResult(
            text=text,
            category=best_category,
            severity=severity,
            confidence=confidence,
            incident_type=intent,
            matched_keywords=best_matches,
            remediation=category_data["remediation"],
            references=references,
            generated_response=generated_response,
        )

    def detect_threat(self, text: str) -> tuple[str, str]:
        """
        Backward-compatible helper matching the original API.
        Returns (category_name, severity_label) e.g. ("Malware Infection", "High").
        """
        result = self.analyze(text)
        severity_label = result.severity.value.split(" ", 1)[1]  # strip emoji
        return (result.category, severity_label)


# ==============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTIONS (drop-in replacement for the old function)
# ==============================================================================

_default_detector = ThreatDetector()


def detect_threat(text: str) -> tuple[str, str]:
    """Drop-in replacement for the original detect_threat(text) function."""
    return _default_detector.detect_threat(text)


def analyze_threat(text: str) -> ThreatAnalysisResult:
    """Full analysis with severity, confidence score, and remediation advice."""
    return _default_detector.analyze(text)


def get_threat_response(text: str):
    """
    Convenience helper returning the RAG-augmented result as a tuple:
    (category, severity_display, confidence, generated_response).

    Example:
        category, severity, confidence, response = get_threat_response(message)
    """
    result = analyze_threat(text)
    return (
        result.category,
        result.severity.value,
        result.confidence,
        result.generated_response or result.remediation,
    )


# ==============================================================================
# CLI — Interactive Mode
# ==============================================================================

BANNER = r"""
    ___    ____     _ _____ __    _      __    __   ___    ____
   /   |  / __/____(_) ___// /_  (_)__  / /___/ /  /   |  /  _/
  / /| | / /_/ ___/ /\__ \/ __ \/ / _ \/ / __  /  / /| |  / /
 / ___ |/ __/ /  / /___/ / / / / /  __/ / /_/ /  / ___ |_/ /
/_/  |_/_/ /_/  /_//____/_/ /_/_/\___/_/\__,_/  /_/  |_/___/

        AfriShield AI — African AI Security Assistant
        Cyber Threat Detection & Response
"""


def run_cli() -> None:
    detector = ThreatDetector()
    print(BANNER)
    print("Describe a security incident to assess (or 'exit' to quit).\n")

    while True:
        try:
            user_input = input("🛡️  Incident > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nStay vigilant. Goodbye! 👋")
            break

        if user_input.lower() in {"exit", "quit"}:
            print("Stay vigilant. Goodbye! 👋")
            break
        if not user_input:
            continue

        result = detector.analyze(user_input)
        print()
        print(result.summary())
        print()


if __name__ == "__main__":
    run_cli()