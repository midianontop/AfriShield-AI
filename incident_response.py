from __future__ import annotations

from typing import Dict, List

_DEFAULT_RESPONSES: List[str] = [
    "Investigate the incident further.",
    "Monitor systems for suspicious activity.",
    "Follow cybersecurity best practices.",
]

_CATEGORY_ALIASES: Dict[str, str] = {
    "account compromise": "Account/Device Compromise",
    "device compromise": "Account/Device Compromise",
    "account/device compromise": "Account/Device Compromise",
    "account compromised": "Account/Device Compromise",
    "device compromised": "Account/Device Compromise",
    "compromised account": "Account/Device Compromise",
    "account takeover": "Account/Device Compromise",
    "hacked account": "Account/Device Compromise",
    "whatsapp takeover": "Account/Device Compromise",
    "ransomware": "Ransomware Attack",
    "ransomware attack": "Ransomware Attack",
    "malware": "Malware Infection",
    "malware infection": "Malware Infection",
    "phishing": "Phishing Attack",
    "phishing attack": "Phishing Attack",
    "scam": "Scam/Fraud",
    "fraud": "Scam/Fraud",
    "scam/fraud": "Scam/Fraud",
    "419 scam": "Scam/Fraud",
    "sim swap": "SIM Swap Fraud",
    "sim swap fraud": "SIM Swap Fraud",
    "sim swapped": "SIM Swap Fraud",
    "authentication issue": "Authentication Issue",
    "auth issue": "Authentication Issue",
    "login issue": "Authentication Issue",
    "data breach": "Data Breach",
    "breach": "Data Breach",
    "general security question": "General Security Question",
    "security question": "General Security Question",
    "question": "General Security Question",
}

_RESPONSES: Dict[str, List[str]] = {
    "Account/Device Compromise": [
        "Disconnect affected devices from the internet.",
        "Change all passwords immediately.",
        "Enable multi-factor authentication (MFA).",
        "Review login history for suspicious activity.",
        "Log out of all active sessions.",
        "Run a malware scan on the affected device.",
        "Notify contacts if your account was abused.",
    ],
    "Ransomware Attack": [
        "Disconnect infected systems immediately.",
        "Do not pay the ransom.",
        "Identify affected files and systems.",
        "Restore data from clean backups.",
        "Report the incident to authorities.",
    ],
    "Malware Infection": [
        "Disconnect the device from the internet.",
        "Run a full malware scan.",
        "Remove suspicious applications.",
        "Update your operating system.",
        "Restore files from backups if necessary.",
    ],
    "Phishing Attack": [
        "Do not click suspicious links.",
        "Change passwords for affected accounts.",
        "Enable multi-factor authentication (MFA).",
        "Report the phishing message.",
        "Monitor accounts for unusual activity.",
    ],
    "Scam/Fraud": [
        "Stop communication with the suspected scammer.",
        "Do not send money or personal information.",
        "Report the scam to relevant authorities.",
        "Monitor bank and online accounts.",
        "Warn others about the scam.",
    ],
    "SIM Swap Fraud": [
        "Contact your mobile network provider immediately.",
        "Freeze affected bank accounts if necessary.",
        "Change passwords on critical accounts.",
        "Enable app-based authentication where possible.",
        "Report the incident to authorities.",
    ],
    "Authentication Issue": [
        "Reset your password immediately.",
        "Enable multi-factor authentication (MFA).",
        "Review login history.",
        "Remove unknown devices.",
        "Update recovery information.",
    ],
    "Data Breach": [
        "Change affected passwords immediately.",
        "Monitor accounts for suspicious activity.",
        "Enable multi-factor authentication.",
        "Check whether personal information was exposed.",
        "Notify affected users if applicable.",
    ],
    "General Security Question": [
        "Follow cybersecurity best practices.",
        "Keep systems updated.",
        "Use strong passwords.",
        "Enable multi-factor authentication (MFA).",
        "Stay alert for suspicious activity.",
    ],
}


def _normalize_threat_type(threat_type: str | None) -> str:
    if not threat_type:
        return "General Security Question"

    normalized = threat_type.strip().lower()
    return _CATEGORY_ALIASES.get(normalized, threat_type.strip())


def get_incident_response(threat_type: str | None) -> List[str]:
    """Return recommended mitigation steps for a detected incident category."""
    category = _normalize_threat_type(threat_type)
    return _RESPONSES.get(category, _DEFAULT_RESPONSES)
