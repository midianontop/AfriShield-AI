def detect_scam(text):

    text = text.lower()

    if (
        "bvn" in text
        or "verify your account" in text
        or "click here" in text
    ):
        return "Phishing Scam"

    elif (
        "registration fee" in text
        or "pay before interview" in text
        or "job offer" in text
    ):
        return "Job Scam"

    elif (
        "atm card" in text
        or "bank details" in text
        or "otp" in text
    ):
        return "Financial Fraud"

    return None