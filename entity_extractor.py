"""
================================================================================
  AfriShield AI
  Entity Extractor
================================================================================

  Pulls structured signals — monetary amounts, bank/fintech names, OTP-code
  mentions, device/platform mentions — out of free-text incident reports,
  and combines them into a single 0-100 "severity_hint" score.

  threat_detector.py uses this as a secondary signal alongside its own
  keyword-based scoring, specifically to catch real incidents described
  without hitting any of the rule engine's exact keyword phrases — e.g.
  "9000 naira left my GTBank account and I never approved it" doesn't
  contain the literal phrase "unauthorized transaction", but the presence
  of an amount + a bank + explicit non-consent language makes it obviously
  one.

  Design note on the dropped bare-digit OTP pattern: an earlier draft of
  this module matched any bare 4-6 digit number as a possible OTP code.
  That was removed — it produced false positives on years ("in 2024 my
  account was hacked"), phone number fragments, and amounts. OTP detection
  here is intentionally conservative: it only fires on explicit contextual
  words (otp, verification code, one-time password, pin code), not on
  digit patterns alone.

  Author  : Midian
  Module  : entity_extractor.py
  Version : 1.0.0
================================================================================
"""

from __future__ import annotations

import re

# Known Nigerian/African banks and fintech platforms, aligned with the
# banking vocabulary already established in threat_detector.py's Financial
# Fraud category and this project's Hausa/Yoruba/Igbo/Swahili glossaries.
KNOWN_BANKS = [
    "gtbank", "gt bank", "access bank", "uba", "first bank", "zenith bank",
    "fidelity bank", "union bank", "stanbic", "wema bank", "polaris bank",
    "opay", "palmpay", "moniepoint", "kuda", "paga",
    "m-pesa", "mpesa", "airtel money", "mtn momo",
]

DEVICE_WORDS = [
    "phone", "laptop", "computer", "pc", "sim card", "sim", "router",
    "tablet", "iphone", "android", "whatsapp", "email", "gmail",
    "facebook", "instagram",
]

_AMOUNT_RE = re.compile(
    r"""
    (?:₦|\$|usd\s?|ngn\s?)[\d,]+(?:\.\d+)?          # ₦5000, $100, USD 200, NGN 500
    |
    [\d,]+(?:\.\d+)?\s?(?:naira|dollars?|usd|ngn|k\b)  # 5000 naira, 10k, 200 dollars
    """,
    re.IGNORECASE | re.VERBOSE,
)

_OTP_CONTEXT_RE = re.compile(
    r"\b(?:otp|one[\s-]?time[\s-]?password|verification\s?code|pin\s?code)\b",
    re.IGNORECASE,
)

_LOSS_LANGUAGE_RE = re.compile(
    r"\b(stolen|withdrawn|debited|unauthorized|without\s+my\s+permission|without\s+my\s+consent)\b",
    re.IGNORECASE,
)


def _find_amounts(text: str) -> list[str]:
    return [m.group(0).strip() for m in _AMOUNT_RE.finditer(text)]


def _find_banks(text_lower: str) -> list[str]:
    return [b for b in KNOWN_BANKS if b in text_lower]


def _find_otp_mentions(text: str) -> list[str]:
    return [m.group(0).strip() for m in _OTP_CONTEXT_RE.finditer(text)]


def _find_devices(text_lower: str) -> list[str]:
    return [d for d in DEVICE_WORDS if re.search(rf"\b{re.escape(d)}\b", text_lower)]


def _compute_severity_hint(
    amounts: list[str], banks: list[str], otp_hits: list[str],
    devices: list[str], text_lower: str,
) -> float:
    """
    Combine found entities into a single 0-100 "how concrete does this
    look" score. Heuristic, not a trained model — weights are tuned to
    the thresholds threat_detector.py actually checks: >=40 triggers
    category inference when no keyword matched, >=65 escalates severity
    one level, >=90 escalates two levels. Adjust these constants together
    with those thresholds if you retune one side.
    """
    score = 0.0

    if amounts:
        score += 35 if len(amounts) == 1 else 45
    if banks:
        score += 25
    if otp_hits:
        score += 30
    if devices:
        score += 10
    if _LOSS_LANGUAGE_RE.search(text_lower):
        score += 15

    return min(100.0, score)


def extract_entities(text: str) -> dict:
    """
    Extract structured signals from free text.

    Returns a dict with:
      amounts               : list[str]  matched monetary amounts
      banks                 : list[str]  matched bank/fintech names
      otp_codes_or_mentions : list[str]  matched OTP-context phrases
      devices                : list[str]  matched device/platform mentions
      severity_hint          : float      0-100 combined heuristic score

    Never raises: empty/whitespace input returns an all-empty, zero-hint
    result rather than erroring, since threat_detector.analyze() treats
    this purely as a secondary signal that should degrade gracefully —
    matching the resilience pattern used throughout this project (a
    missing/failed secondary signal should never take down the primary
    keyword-based classification).
    """
    if not text or not text.strip():
        return {
            "amounts": [], "banks": [], "otp_codes_or_mentions": [],
            "devices": [], "severity_hint": 0.0,
        }

    text_lower = text.lower()
    amounts = _find_amounts(text)
    banks = _find_banks(text_lower)
    otp_hits = _find_otp_mentions(text)
    devices = _find_devices(text_lower)
    severity_hint = _compute_severity_hint(amounts, banks, otp_hits, devices, text_lower)

    return {
        "amounts": amounts,
        "banks": banks,
        "otp_codes_or_mentions": otp_hits,
        "devices": devices,
        "severity_hint": severity_hint,
    }


if __name__ == "__main__":
    samples = [
        "9000 naira left my GTBank account and I never approved it",
        "someone sent me an otp code and asked me to share it",
        "my phone and whatsapp got hacked yesterday",
        "what is phishing?",
        "in 2024 I read an article about phishing",  # regression check: no false OTP hit on the year
    ]
    for s in samples:
        print(s, "->", extract_entities(s))