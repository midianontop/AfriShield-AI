"""AfriShield AI — threat category database."""

from .enums import Severity


THREAT_CATEGORIES = {
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
            "opay": 2, "palmpay": 2, "419 scam": 3,
            "advance fee fraud": 3, "m-pesa": 2, "mpesa": 2,
            "m-pesa fraud": 3, "eft fraud": 3,
            "electronic funds transfer fraud": 3,
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
