from scam_detector import detect_scam

message = """
Congratulations!
Your BVN will be suspended.
Click here to verify.
"""

print(
    detect_scam(message)
)