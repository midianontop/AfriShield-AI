"""
================================================================================
  AFRISHIELD AI  —  African AI Security Assistant
  Scam & Fraud Detection Engine
================================================================================

  Designed for the realities of African digital life — mobile money fraud,
  BVN/NIN phishing, fake job offers, POS agent scams, romance & crypto
  fraud, and more.

  Author  : Midian
  Module  : scam_detector.py
  Version : 2.0.0
================================================================================
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


# ==============================================================================
# RISK LEVELS
# ==============================================================================

class RiskLevel(Enum):
    SAFE = "✅ SAFE"
    LOW = "🟡 LOW RISK"
    MEDIUM = "🟠 MEDIUM RISK"
    HIGH = "🔴 HIGH RISK"
    CRITICAL = "🚨 CRITICAL RISK"


# ==============================================================================
# SCAM CATEGORY DEFINITIONS
# ==============================================================================
# Each category carries:
#   - keywords : phrases/words that raise suspicion (weighted by severity)
#   - advice   : practical, locally-relevant guidance for the user
# ==============================================================================

SCAM_CATEGORIES: dict[str, dict] = {
    "Phishing Scam": {
        "keywords": {
            "verify your account": 3, "click here": 2, "login here": 2,
            "update your account": 2, "account suspended": 3,
            "confirm your details": 3, "bvn": 3, "nin": 3,
            "reset your password": 2, "bank verification": 3,
            "verify now": 2, "urgent action required": 3,
            "suspicious activity": 2, "unusual login": 2,
            "your account will be blocked": 3, "kyc update": 3,
        },
        "advice": (
            "Never click links or share your BVN, NIN, or login details "
            "from unsolicited messages. Contact your bank directly using "
            "the number on the back of your card or their official app."
        ),
    },
    "Job Scam": {
        "keywords": {
            "registration fee": 3, "pay before interview": 3, "job offer": 1,
            "employment offer": 1, "recruitment fee": 3, "processing fee": 2,
            "guaranteed job": 2, "work from home and earn": 2,
            "salary upfront": 2, "no interview needed": 2,
            "send your cv and pay": 3, "training fee": 2,
        },
        "advice": (
            "Legitimate employers never ask you to pay for a job, "
            "interview, or training. Verify the company's registration "
            "and never send money to secure employment."
        ),
    },
    "Loan Scam": {
        "keywords": {
            "instant loan": 2, "loan approval fee": 3, "pay before loan": 3,
            "guaranteed loan": 2, "quick loan": 1, "loan processing fee": 3,
            "loan application fee": 3, "unlock your loan": 2,
        },
        "advice": (
            "Legitimate lenders do not require upfront payments "
            "before releasing a loan. Verify the lender's "
            "registration and avoid paying processing fees "
            "to unknown individuals."
        ),
    },
    "Financial / Mobile Money Fraud": {
        "keywords": {
            "atm card": 2, "bank details": 2, "otp": 3,
            "one time password": 3, "pin number": 3, "account number": 1,
            "send your card": 3, "transfer fee": 2, "bank account": 1,
            "mobile money pin": 3, "momo pin": 3, "airtime pin": 2,
            "sim swap": 3, "agent code": 2, "pos agent": 1,
            "reversal error": 2, "wrong transfer": 2,
        },
        "advice": (
            "Never share your OTP, PIN, or card details with anyone — "
            "not even someone claiming to be your bank, network provider, "
            "or a mobile money agent. Banks never ask for your PIN or OTP."
        ),
    },
    "Lottery / Prize Scam": {
        "keywords": {
            "you won": 2, "congratulations winner": 2, "claim your prize": 3,
            "lottery winner": 3, "cash prize": 2, "million naira": 2,
            "jackpot": 2, "you have been selected": 2,
            "shipping fee to claim": 3, "clearance fee": 3,
        },
        "advice": (
            "If you didn't enter a competition, you can't win it. "
            "Never pay a 'clearance' or 'shipping' fee to release a prize."
        ),
    },
    "Crypto / Investment Scam": {
        "keywords": {
            "double your bitcoin": 3, "guaranteed profit": 3,
            "crypto investment": 2, "send crypto": 2,
            "investment opportunity": 1, "100% return": 3,
            "risk free investment": 3, "forex trading guaranteed": 3,
            "double your money": 3, "ponzi": 3, "mmm": 2,
            "invest today and earn": 2,
        },
        "advice": (
            "There is no such thing as a 'risk-free' or 'guaranteed' "
            "investment return. Research any platform thoroughly and "
            "verify SEC/CBN registration before investing."
        ),
    },
    "Romance Scam": {
        "keywords": {
            "send me money": 3, "i love you but": 2,
            "help me financially": 2, "emergency money": 2,
            "gift card": 2, "stuck at customs": 3,
            "need money to fly to you": 3, "medical emergency abroad": 2,
        },
        "advice": (
            "Be cautious of online partners you've never met in person "
            "who ask for money, gift cards, or financial help — "
            "especially during a 'crisis'."
        ),
    },
    "Social Media Scam": {
        "keywords": {
            "facebook giveaway": 3, "instagram verification": 2,
            "whatsapp investment group": 3, "tiktok reward": 2,
            "social media prize": 2, "follow and earn": 2,
            "fake influencer": 3, "account verification required": 3,
        },
        "advice": (
            "Verify offers directly through official social media "
            "accounts. Be cautious of giveaways, rewards, or "
            "investment opportunities promoted through private messages."
        ),
    },
    "AI / Deepfake Scam": {
        "keywords": {
            "deepfake": 3, "voice clone": 3, "ai generated video": 2,
            "fake celebrity endorsement": 3, "synthetic voice": 3,
            "fake video call": 3, "ai investment scheme": 3,
            "celebrity crypto investment": 3,
        },
        "advice": (
            "Verify requests for money or sensitive information "
            "through a second trusted communication channel. "
            "AI-generated voices and videos can be used to impersonate "
            "friends, family members, or public figures."
        ),
    },
}


# ==============================================================================
# RESULT OBJECT
# ==============================================================================

@dataclass
class ScamAnalysisResult:
    text: str
    risk_level: RiskLevel
    confidence: float
    matched_categories: dict[str, list[str]] = field(default_factory=dict)
    top_category: str | None = None
    advice: str | None = None
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def summary(self) -> str:
        lines = [
            "=" * 60,
            "  AFRISHIELD AI — Scam Analysis Report",
            "=" * 60,
            f"Risk Level     : {self.risk_level.value}",
            f"Confidence     : {self.confidence:.0f}%",
            f"Category       : {self.top_category or 'None detected'}",
        ]
        if self.matched_categories:
            lines.append("Matched Signals:")
            for cat, hits in self.matched_categories.items():
                lines.append(f"  • {cat}: {', '.join(hits)}")
        if self.advice:
            lines.append(f"\nRecommendation : {self.advice}")
        lines.append("=" * 60)
        return "\n".join(lines)


# ==============================================================================
# CORE DETECTOR
# ==============================================================================

class ScamDetector:
    """
    AfriShield AI's core scam-detection engine.

    Scans free-text (SMS, WhatsApp, email, social media messages) for
    patterns commonly used in scams targeting African users, and returns
    a risk-scored analysis with actionable advice.
    """

    def __init__(self, categories: dict[str, dict] | None = None):
        self.categories = categories or SCAM_CATEGORIES

    @staticmethod
    def _normalize(text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"\s+", " ", text)
        return text

    def _score_text(self, text: str) -> dict[str, tuple[int, list[str]]]:
        """Return {category: (score, matched_keywords)} for every category hit."""
        results: dict[str, tuple[int, list[str]]] = {}
        for category, data in self.categories.items():
            score = 0
            matches: list[str] = []
            for keyword, weight in data["keywords"].items():
                pattern = r"\b" + re.escape(keyword) + r"\b"
                if re.search(pattern, text):
                    score += weight
                    matches.append(keyword)
            if matches:
                results[category] = (score, matches)
        return results

    @staticmethod
    def _score_to_risk(score: int) -> tuple[RiskLevel, float]:
        """Map a cumulative keyword score to a risk level + confidence %."""
        if score == 0:
            return RiskLevel.SAFE, 0.0
        elif score <= 2:
            return RiskLevel.LOW, 35.0
        elif score <= 5:
            return RiskLevel.MEDIUM, 65.0
        elif score <= 8:
            return RiskLevel.HIGH, 85.0
        else:
            return RiskLevel.CRITICAL, 95.0

    def analyze(self, text: str) -> ScamAnalysisResult:
        """Analyze a message and return a full ScamAnalysisResult."""
        if not text or not text.strip():
            return ScamAnalysisResult(
                text=text,
                risk_level=RiskLevel.SAFE,
                confidence=0.0,
            )

        normalized = self._normalize(text)
        category_scores = self._score_text(normalized)

        if not category_scores:
            return ScamAnalysisResult(
                text=text,
                risk_level=RiskLevel.SAFE,
                confidence=0.0,
            )

        top_category = max(category_scores, key=lambda c: category_scores[c][0])
        top_score = category_scores[top_category][0]
        matched_category_count = len(category_scores)

        risk_level, confidence = self._score_to_risk(top_score)

        # Escalate if several scam categories match
        if matched_category_count >= 3:
            confidence = min(confidence + 10, 99.0)

        return ScamAnalysisResult(
            text=text,
            risk_level=risk_level,
            confidence=confidence,
            matched_categories={cat: hits for cat, (_, hits) in category_scores.items()},
            top_category=top_category,
            advice=self.categories[top_category]["advice"],
        )

    def detect_scam(self, text: str) -> str | None:
        """
        Backward-compatible helper matching the original API.
        Returns the top matching category name, or None if the text looks safe.
        """
        result = self.analyze(text)
        return result.top_category


# ==============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTION (drop-in replacement for the old function)
# ==============================================================================

_default_detector = ScamDetector()


def detect_scam(text: str) -> str | None:
    """Drop-in replacement for the original detect_scam(text) function."""
    return _default_detector.detect_scam(text)


def analyze_message(text: str) -> ScamAnalysisResult:
    """Full analysis with risk level, confidence score, and advice."""
    return _default_detector.analyze(text)


def get_scam_risk(text: str):
    """
    Convenience helper returning (category, risk_level_display, confidence).
    Example:
        category, risk, confidence = get_scam_risk(message)
    """
    result = analyze_message(text)
    return (
        result.top_category,
        result.risk_level.value,
        result.confidence,
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
        Protecting you from scams, phishing & fraud
"""


def run_cli() -> None:
    detector = ScamDetector()
    print(BANNER)
    print("Type a message to check (or 'exit' to quit).\n")

    while True:
        try:
            user_input = input("📩 Message > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nStay safe out there. Goodbye! 👋")
            break

        if user_input.lower() in {"exit", "quit"}:
            print("Stay safe out there. Goodbye! 👋")
            break
        if not user_input:
            continue

        result = detector.analyze(user_input)
        print()
        print(result.summary())
        print()


if __name__ == "__main__":
    run_cli()