import json
import os
from datetime import datetime

LOG_FILE = "incident_logs.json"


def save_incident(
    question,
    threat,
    severity,
    confidence
):

    incident = {
        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "question": question,
        "threat": threat,
        "severity": severity,
        "confidence": confidence
    }

    if os.path.exists(LOG_FILE):

        try:
            with open(LOG_FILE, "r") as f:
                logs = json.load(f)

        except:
            logs = []

    else:
        logs = []

    logs.append(incident)

    with open(LOG_FILE, "w") as f:
        json.dump(
            logs,
            f,
            indent=4
        )