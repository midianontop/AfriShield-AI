"""AfriShield AI — threat detector enums."""

from enum import Enum


class Severity(Enum):
    LOW = "🟢 Low"
    MEDIUM = "🟡 Medium"
    HIGH = "🟠 High"
    CRITICAL = "🔴 Critical"

    @property
    def rank(self) -> int:
        return {
            Severity.LOW: 0,
            Severity.MEDIUM: 1,
            Severity.HIGH: 2,
            Severity.CRITICAL: 3,
        }[self]

    @classmethod
    def from_rank(cls, rank: int) -> "Severity":
        rank = max(0, min(rank, 3))
        return (cls.LOW, cls.MEDIUM, cls.HIGH, cls.CRITICAL)[rank]


class IncidentType(Enum):
    ACTIVE_INCIDENT = "🚨 Active Incident"
    SECURITY_QUESTION = "❓ Security Question"


class Intent(Enum):
    REPORT_INCIDENT = "Report Incident"
    ASK_SECURITY_QUESTION = "Ask Security Question"
    SCAM_CHECK = "Scam Check"
    PHISHING = "Phishing"
    ACCOUNT_COMPROMISE = "Account Compromise"
    DEVICE_INFECTED = "Device Infected"
    PASSWORD_RESET = "Password Reset"
    MONEY_STOLEN = "Money Stolen"
    WHATSAPP_HACKED = "WhatsApp Hacked"
    EMAIL_COMPROMISED = "Email Compromised"
    RECOVERY_REQUEST = "Recovery Request"
    SAFETY_TIPS = "Safety Tips"
    GENERAL_CHAT = "General Chat"
    GREETING = "Greeting"
    THANK_YOU = "Thank You"
    GOODBYE = "Goodbye"
    UNKNOWN = "Unknown"
