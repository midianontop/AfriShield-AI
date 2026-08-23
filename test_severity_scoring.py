import unittest

from threat_detector import ThreatDetector, Severity


def run_analysis(text, user_id=None):
    detector = ThreatDetector()
    return detector.analyze(text, user_id=user_id)


class SeverityScoringTests(unittest.TestCase):
    def test_otp_and_account_hacked_escalates(self):
        text = "My GTBank account was hacked and they asked for my OTP 123456 and took ₦5,000"
        r = run_analysis(text)
        self.assertIn(r.severity, (Severity.HIGH, Severity.CRITICAL))
        self.assertGreater(r.confidence, 70)

    def test_money_stolen_raises_severity(self):
        text = "Someone withdrew ₦20000 from my account without permission"
        r = run_analysis(text)
        self.assertIn(r.severity, (Severity.MEDIUM, Severity.HIGH))
        self.assertGreater(r.confidence, 50)


if __name__ == '__main__':
    unittest.main()
