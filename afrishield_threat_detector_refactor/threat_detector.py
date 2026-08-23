"""AfriShield AI — Cyber Threat Detection Engine."""

from __future__ import annotations

import difflib
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import lru_cache

from entity_extractor import extract_entities
from conversation_memory import memory as conversation_memory

from .config import (
    CONFIDENCE_BASE, CONFIDENCE_ENTITY_WEIGHT, CONFIDENCE_PER_SCORE,
    CONFIDENCE_SCORE_WEIGHT, CONFIDENCE_THRESHOLD, ENTITY_FALLBACK_HINT,
    FUZZY_MATCH_THRESHOLD, HIGH_HINT, MAX_CONFIDENCE, MEDIUM_HINT,
    MIN_THREAT_SCORE, PHRASE_SLACK,
)
from .enums import IncidentType, Intent, Severity
from .threat_database import THREAT_CATEGORIES

logger = logging.getLogger("afrishield_ai.threat_detector")


# ============================== INTENT ======================================

QUESTION_WORDS = {
    "what", "how", "why", "when", "who", "which", "can", "could",
    "does", "do", "is", "are", "should", "would", "explain", "define",
}

STRONG_INCIDENT_MARKERS = (
    "my ", "our ", "i've", "i have", "i'm", "i am", "we're", "we are",
    "currently", "right now", "just happened", "just now",
)

WEAK_INCIDENT_MARKERS = (
    "someone", "they stole", "they hacked", "help me", "please help", "urgent",
)

STRONG_INCIDENT_RE = re.compile(
    r"(?<!\w)(?:" + "|".join(map(re.escape, STRONG_INCIDENT_MARKERS)) + r")(?!\w)"
)

INTENT_KEYWORDS = {
    Intent.REPORT_INCIDENT: ["my account", "i was hacked", "they hacked", "account was hacked", "stolen my", "someone stole"],
    Intent.ASK_SECURITY_QUESTION: ["what is", "how do i", "how to", "why is", "define", "explain"],
    Intent.SCAM_CHECK: ["is this a scam", "scam", "suspicious", "verify this", "is this legit"],
    Intent.PHISHING: ["phishing", "otp", "one time password", "verification code", "login link"],
    Intent.ACCOUNT_COMPROMISE: ["account compromised", "account hacked", "logged in from", "unauthorized access"],
    Intent.DEVICE_INFECTED: ["malware", "virus", "infected", "apps installing themselves", "pop up ads"],
    Intent.PASSWORD_RESET: ["reset password", "forgot password", "change my password"],
    Intent.MONEY_STOLEN: ["money stolen", "unauthorized transaction", "lost money", "cash missing"],
    Intent.WHATSAPP_HACKED: ["whatsapp hacked", "whatsapp takeover", "whatsapp account"],
    Intent.EMAIL_COMPROMISED: ["email hacked", "email compromised", "gmail hacked"],
    Intent.RECOVERY_REQUEST: ["help me recover", "how can i recover", "i need to recover"],
    Intent.SAFETY_TIPS: ["stay safe", "safety tips", "how to stay safe", "security best practices"],
    Intent.GENERAL_CHAT: ["hello", "hi", "how are you", "just asking"],
    Intent.GREETING: ["hello", "hi", "good morning", "good evening"],
    Intent.THANK_YOU: ["thank you", "thanks", "ty"],
    Intent.GOODBYE: ["bye", "goodbye", "see you"],
}

INTENT_PRIORITY = [
    Intent.RECOVERY_REQUEST, Intent.WHATSAPP_HACKED, Intent.REPORT_INCIDENT,
    Intent.ACCOUNT_COMPROMISE, Intent.PHISHING, Intent.SCAM_CHECK,
    Intent.ASK_SECURITY_QUESTION, Intent.SAFETY_TIPS, Intent.GREETING,
    Intent.THANK_YOU, Intent.GOODBYE, Intent.GENERAL_CHAT,
]


def _is_question(text: str) -> bool:
    words = text.split()
    first = words[0].strip("?.,!") if words else ""
    return text.endswith("?") or first in QUESTION_WORDS


def detect_user_intent(text: str) -> tuple[Intent, float]:
    if not text or not text.strip():
        return Intent.UNKNOWN, 0.0

    normalized = text.strip().lower()
    tokens = _tokenize(normalized)
    scores = {}

    for intent, phrases in INTENT_KEYWORDS.items():
        for phrase in phrases:
            if _phrase_matches(tokens, phrase):
                scores[intent] = scores.get(intent, 0) + 1

    if not scores:
        if _is_question(normalized):
            return Intent.ASK_SECURITY_QUESTION, 60.0
        if normalized.startswith(("hi", "hello", "hey")):
            return Intent.GREETING, 85.0
        return Intent.UNKNOWN, 0.0

    highest = max(scores.values())
    candidates = [i for i, score in scores.items() if score == highest]
    best = next((i for i in INTENT_PRIORITY if i in candidates), candidates[0])
    return best, min(99.0, 50.0 + scores[best] * 20.0)


def _detect_incident_type(text: str) -> IncidentType:
    normalized = text.strip().lower()

    if not normalized or _is_question(normalized):
        return IncidentType.SECURITY_QUESTION
    if STRONG_INCIDENT_RE.search(normalized):
        return IncidentType.ACTIVE_INCIDENT
    return IncidentType.ACTIVE_INCIDENT


_detect_intent = _detect_incident_type


# ================================ NLP =======================================

SUFFIXES = ("ingly", "edly", "ing", "edness", "ed", "es")


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", text.lower())


def _stem(word: str) -> str:
    for suffix in SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[:-len(suffix)]
    return word


@lru_cache(maxsize=4096)
def _tokens_match(a: str, b: str) -> bool:
    if a == b or _stem(a) == _stem(b):
        return True
    if abs(len(a) - len(b)) <= 2:
        return difflib.SequenceMatcher(None, a, b).ratio() >= FUZZY_MATCH_THRESHOLD
    return False


def _phrase_matches(tokens: list[str], keyword: str, slack: int = PHRASE_SLACK) -> bool:
    keyword_tokens = _tokenize(keyword)
    count = len(keyword_tokens)

    if not keyword_tokens or count > len(tokens):
        return False

    if count == 1:
        return any(_tokens_match(t, keyword_tokens[0]) for t in tokens)

    for start in range(len(tokens)):
        window = tokens[start:start + count + slack]
        if len(window) < count:
            break

        remaining = list(window)
        for target in keyword_tokens:
            index = next((i for i, token in enumerate(remaining) if _tokens_match(token, target)), None)
            if index is None:
                break
            remaining.pop(index)
        else:
            return True

    return False


# =========================== LOCAL KNOWLEDGE ================================

class ThreatKnowledgeBase:
    REFERENCES = {
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
        return self.REFERENCES.get(category, [])[:top_k]


class ThreatResponseGenerator:
    def generate(self, text, category, severity, references, remediation) -> str:
        raise NotImplementedError


class TemplateResponseGenerator(ThreatResponseGenerator):
    def generate(self, text, category, severity, references, remediation) -> str:
        response = f"This looks like a {category} case ({severity.value} severity). {remediation}"
        if references:
            response += " " + " ".join(f"[{ref}]" for ref in references)
        return response


# ============================== RESULT ======================================

@dataclass
class ThreatAnalysisResult:
    text: str
    category: str
    severity: Severity
    confidence: float
    incident_type: IncidentType = IncidentType.ACTIVE_INCIDENT
    user_intent: Intent = Intent.UNKNOWN
    intent_confidence: float = 0.0
    matched_keywords: list[str] = field(default_factory=list)
    remediation: str = ""
    references: list[str] = field(default_factory=list)
    generated_response: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    entities: dict = field(default_factory=dict)

    def summary(self) -> str:
        lines = [
            "=" * 60,
            "  AFRISHIELD AI — Threat Analysis Report",
            "=" * 60,
            f"Incident Type  : {self.incident_type.value}",
            f"User Intent    : {self.user_intent.value} ({self.intent_confidence:.0f}%)",
            f"Category       : {self.category}",
            f"Severity       : {self.severity.value}",
            f"Confidence     : {self.confidence:.0f}%",
        ]
        if self.matched_keywords:
            lines.append(f"Matched Signals: {', '.join(self.matched_keywords)}")
        if self.references:
            lines.append("References:")
            lines.extend(f"  • {ref}" for ref in self.references)
        if self.generated_response:
            lines.append(f"\nAfriShield AI Response:\n  {self.generated_response}")
        elif self.remediation:
            lines.append(f"\nRecommended Action:\n  {self.remediation}")
        lines.append("=" * 60)
        return "\n".join(lines)


# ============================== DETECTOR ====================================

NO_SIGNAL_REMEDIATION = (
    "No specific threat indicators found. If you suspect something is wrong, "
    "describe the exact symptoms (unexpected messages, pop-ups, transactions, "
    "etc.) for a more precise assessment."
)

LOW_CONFIDENCE_REMEDIATION = (
    "This appears to be a general security question rather than an active "
    "incident report. Describe the exact problem, including any impacted "
    "accounts, devices, or suspicious transactions, for a more accurate assessment."
)


class ThreatDetector:
    def __init__(self, categories=None, knowledge_base=None, generator=None):
        self.categories = categories or THREAT_CATEGORIES
        self.knowledge_base = knowledge_base or ThreatKnowledgeBase()
        self.generator = generator or TemplateResponseGenerator()

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(r"\s+", " ", text.lower().strip())

    def _score_category(self, tokens, keywords):
        score = 0
        matches = []
        for keyword, weight in keywords.items():
            if _phrase_matches(tokens, keyword):
                score += weight
                matches.append(keyword)
        return score, matches

    def _score_categories(self, tokens):
        best_category = None
        best_score = 0
        best_matches = []

        for category, data in self.categories.items():
            score, matches = self._score_category(tokens, data["keywords"])
            if score > best_score:
                best_category = category
                best_score = score
                best_matches = matches

        if best_category and best_score >= MIN_THREAT_SCORE:
            return best_category, best_score, best_matches
        return None, best_score, []

    @staticmethod
    def _entity_fallback(entities, floor_score=0):
        hint = entities.get("severity_hint", 0)
        if hint < ENTITY_FALLBACK_HINT:
            return None, 0, []

        if entities.get("amounts") or entities.get("banks"):
            return "Financial Fraud", max(floor_score, int(hint / 10)), ["financial signal detected"]
        if entities.get("otp_codes_or_mentions"):
            return "Phishing Attack", max(floor_score, int(hint / 10)), ["otp detected"]
        if entities.get("devices"):
            return "Account/Device Compromise", max(floor_score, int(hint / 10)), ["device signal detected"]

        return "Financial Fraud", max(floor_score, int(hint / 15)), ["entity-derived signal"]

    @staticmethod
    def _confidence_from_score(score):
        if score <= 0:
            return 0.0
        return round(min(MAX_CONFIDENCE, CONFIDENCE_BASE + score * CONFIDENCE_PER_SCORE), 1)

    def _calculate_confidence(self, score, entities):
        lexical = self._confidence_from_score(score)
        hint = float(entities.get("severity_hint", 0))
        combined = round(
            min(MAX_CONFIDENCE, lexical * CONFIDENCE_SCORE_WEIGHT + hint * CONFIDENCE_ENTITY_WEIGHT),
            1,
        )
        return max(lexical, combined)

    @staticmethod
    def _calculate_severity(base, incident_type, confidence, matches, entities):
        severity = base

        if incident_type != IncidentType.SECURITY_QUESTION:
            if confidence >= CONFIDENCE_THRESHOLD and len(matches) >= 2:
                severity = Severity.from_rank(base.rank + 1)

        hint = entities.get("severity_hint", 0)
        if hint >= HIGH_HINT:
            severity = Severity.from_rank(severity.rank + 2)
        elif hint >= MEDIUM_HINT:
            severity = Severity.from_rank(severity.rank + 1)

        return severity

    @staticmethod
    def _build_result(text, category, severity, confidence=0.0,
                      incident_type=IncidentType.SECURITY_QUESTION,
                      user_intent=Intent.UNKNOWN, intent_confidence=0.0,
                      matched_keywords=None, remediation="",
                      references=None, generated_response="", entities=None):
        return ThreatAnalysisResult(
            text=text,
            category=category,
            severity=severity,
            confidence=confidence,
            incident_type=incident_type,
            user_intent=user_intent,
            intent_confidence=intent_confidence,
            matched_keywords=matched_keywords or [],
            remediation=remediation,
            references=references or [],
            generated_response=generated_response,
            entities=entities or {},
        )

    @staticmethod
    def _store_memory(user_id, text, entities, intent, intent_confidence, severity, confidence):
        if not user_id:
            return
        try:
            conversation_memory.add_message(
                user_id,
                text,
                {
                    "entities": entities,
                    "user_intent": intent,
                    "intent_confidence": intent_confidence,
                    "severity": severity,
                    "confidence": confidence,
                },
            )
        except Exception as exc:
            logger.debug("Memory persistence failed: %s", exc)

    def analyze(self, text, user_id=None):
        if not text or not text.strip():
            return self._build_result(text, "No Threat Detected", Severity.LOW)

        normalized = self._normalize(text)
        tokens = _tokenize(normalized)

        incident_type = _detect_incident_type(text)
        user_intent, intent_confidence = detect_user_intent(text)
        entities = extract_entities(text)

        category, score, matches = self._score_categories(tokens)

        if category is None:
            category, score, matches = self._entity_fallback(entities, score)

        if category is None:
            return self._build_result(
                text, "General Security Question", Severity.LOW,
                incident_type=incident_type,
                user_intent=user_intent,
                intent_confidence=intent_confidence,
                remediation=NO_SIGNAL_REMEDIATION,
                entities=entities,
            )

        category_data = self.categories[category]
        confidence = self._calculate_confidence(score, entities)

        if (
            incident_type == IncidentType.SECURITY_QUESTION
            and not STRONG_INCIDENT_RE.search(normalized)
        ):
            return self._build_result(
                text, "General Security Question", Severity.LOW,
                incident_type=incident_type,
                user_intent=user_intent,
                intent_confidence=intent_confidence,
                remediation=LOW_CONFIDENCE_REMEDIATION,
                entities=entities,
            )

        severity = self._calculate_severity(
            category_data["base_severity"],
            incident_type,
            confidence,
            matches,
            entities,
        )

        references = self.knowledge_base.retrieve(category)

        response = self.generator.generate(
            text=text,
            category=category,
            severity=severity,
            references=references,
            remediation=category_data["remediation"],
        )

        result = self._build_result(
            text, category, severity, confidence,
            incident_type, user_intent, intent_confidence,
            matches, category_data["remediation"],
            references, response, entities,
        )

        self._store_memory(
            user_id, text, entities, user_intent,
            intent_confidence, severity, confidence,
        )

        return result

    def detect_threat(self, text):
        result = self.analyze(text)
        return result.category, result.severity.value.split(" ", 1)[1]


_default_detector = ThreatDetector()


def detect_threat(text):
    return _default_detector.detect_threat(text)


def analyze_threat(text, user_id=None):
    return _default_detector.analyze(text, user_id=user_id)


def get_threat_response(text):
    result = analyze_threat(text)
    return (
        result.category,
        result.severity.value,
        result.confidence,
        result.generated_response or result.remediation,
    )
