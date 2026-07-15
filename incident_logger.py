"""
============================================================
 AFRISHIELD AI
 Incident Logging System v2.0
============================================================

 Stores cybersecurity incidents detected by AfriShield AI.

 Compatible with:
 - threat_detector.py v3.1
 - app.py
 - dashboard.py

============================================================
"""

import json
import os
import uuid
from datetime import datetime, timezone


LOG_FILE = "incident_logs.json"



def calculate_risk_score(
    severity,
    confidence
):
    """
    Calculate a simple cybersecurity risk score.
    """

    severity_score = {

        "🟢 Low": 10,
        "🟡 Medium": 40,
        "🟠 High": 70,
        "🔴 Critical": 95

    }


    base = severity_score.get(
        severity,
        0
    )


    try:

        confidence = float(confidence)

    except:

        confidence = 0


    risk = (
        base * 0.6
        +
        confidence * 0.4
    )


    return round(
        min(risk,100),
        1
    )




def load_logs():

    """
    Load existing incident logs.
    """

    if not os.path.exists(LOG_FILE):

        return []


    try:

        with open(
            LOG_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)


    except:

        return []




def save_incident(
    question,
    threat,
    severity,
    confidence,
    scam=None,
    incident_type="Active Incident",
    recommendations=None,
    ai_response=None
):

    """
    Save detected cybersecurity incident.

    Parameters:

    question:
        User reported message

    threat:
        Threat category

    severity:
        Threat severity level

    confidence:
        Detection confidence

    scam:
        Scam category if detected

    incident_type:
        Active Incident / Security Question

    recommendations:
        Response actions

    ai_response:
        Generated AI answer

    """


    incident = {


        "incident_id":

            str(uuid.uuid4())[:8],



        "timestamp":

            datetime.now(
                timezone.utc
            ).isoformat(),



        "user_report":

            question,



        "incident_type":

            incident_type,



        "threat_category":

            threat,



        "severity":

            severity,



        "confidence":

            confidence,



        "risk_score":

            calculate_risk_score(
                severity,
                confidence
            ),



        "scam_detected":

            scam,



        "recommendations":

            recommendations or [],



        "ai_response":

            ai_response

    }



    logs = load_logs()



    logs.append(
        incident
    )



    try:

        with open(
            LOG_FILE,
            "w",
            encoding="utf-8"
        ) as file:


            json.dump(
                logs,
                file,
                indent=4,
                ensure_ascii=False
            )


        return True



    except Exception as error:


        print(
            f"Logging error: {error}"
        )


        return False