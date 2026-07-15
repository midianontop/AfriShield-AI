def get_incident_response(threat_type):

    responses = {

        "Account/Device Compromise": [
            "Disconnect affected device from the internet.",
            "Change all passwords immediately.",
            "Enable Multi-Factor Authentication (MFA).",
            "Review login history for suspicious activity.",
            "Log out of all active sessions.",
            "Run a malware scan on the affected device.",
            "Notify contacts if your account was abused."
        ],

        "Ransomware Attack": [
            "Disconnect infected systems immediately.",
            "Do not pay the ransom.",
            "Identify affected files and systems.",
            "Restore data from clean backups.",
            "Report the incident to authorities."
        ],

        "Malware Infection": [
            "Disconnect the device from the internet.",
            "Run a full malware scan.",
            "Remove suspicious applications.",
            "Update your operating system.",
            "Restore files from backups if necessary."
        ],

        "Phishing Attack": [
            "Do not click suspicious links.",
            "Change passwords for affected accounts.",
            "Enable Multi-Factor Authentication (MFA).",
            "Report the phishing message.",
            "Monitor accounts for unusual activity."
        ],

        "Scam/Fraud": [
            "Stop communication with the suspected scammer.",
            "Do not send money or personal information.",
            "Report the scam to relevant authorities.",
            "Monitor bank and online accounts.",
            "Warn others about the scam."
        ],

        "SIM Swap Fraud": [
            "Contact your mobile network provider immediately.",
            "Freeze affected bank accounts if necessary.",
            "Change passwords on critical accounts.",
            "Enable app-based authentication where possible.",
            "Report the incident to authorities."
        ],

        "Authentication Issue": [
            "Reset your password immediately.",
            "Enable Multi-Factor Authentication (MFA).",
            "Review login history.",
            "Remove unknown devices.",
            "Update recovery information."
        ],

        "Data Breach": [
            "Change affected passwords immediately.",
            "Monitor accounts for suspicious activity.",
            "Enable Multi-Factor Authentication.",
            "Check whether personal information was exposed.",
            "Notify affected users if applicable."
        ],

        "General Security Question": [
            "Follow cybersecurity best practices.",
            "Keep systems updated.",
            "Use strong passwords.",
            "Enable Multi-Factor Authentication (MFA).",
            "Stay alert for suspicious activity."
        ]
    }

    return responses.get(
        threat_type,
        [
            "Investigate the incident further.",
            "Monitor systems for suspicious activity.",
            "Follow cybersecurity best practices."
        ]
    )