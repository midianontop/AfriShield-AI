import unittest

from threat_detector import ThreatDetector, IncidentType, Severity


class ThreatDetectorTests(unittest.TestCase):
    def setUp(self):
        self.detector = ThreatDetector()

    def test_active_incident_with_personal_report(self):
        result = self.detector.analyze(
            "My Whatsapp account was hacked and I need help now."
        )
        self.assertEqual(result.incident_type, IncidentType.ACTIVE_INCIDENT)
        self.assertEqual(result.category, "Account/Device Compromise")
        self.assertGreaterEqual(result.confidence, 35.0)
        self.assertIn("whatsapp hacked", result.matched_keywords)

    def test_security_question_about_ransomware(self):
        result = self.detector.analyze("What is ransomware and how does it work?")
        self.assertEqual(result.incident_type, IncidentType.SECURITY_QUESTION)
        self.assertEqual(result.category, "General Security Question")
        self.assertEqual(result.severity, Severity.LOW)
        self.assertEqual(result.confidence, 0.0)

    def test_weak_marker_without_threat_topic_is_not_active(self):
        result = self.detector.analyze("Someone told me they hacked an account.")
        self.assertEqual(result.incident_type, IncidentType.SECURITY_QUESTION)
        self.assertEqual(result.category, "General Security Question")
        self.assertEqual(result.confidence, 0.0)

    def test_minimum_score_prevents_false_positive(self):
        result = self.detector.analyze("I saw a suspicious email.")
        self.assertEqual(result.category, "General Security Question")
        self.assertEqual(result.severity, Severity.LOW)
        self.assertEqual(result.confidence, 0.0)


if __name__ == "__main__":
    unittest.main()
