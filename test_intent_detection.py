import unittest

from threat_detector import detect_user_intent, Intent


class IntentDetectionTests(unittest.TestCase):
    def test_report_incident(self):
        intent, conf = detect_user_intent("Someone asked for my OTP and my account got hacked")
        self.assertEqual(intent, Intent.REPORT_INCIDENT)
        self.assertGreater(conf, 50)

    def test_general_question(self):
        intent, conf = detect_user_intent("What is phishing and how does it work?")
        self.assertEqual(intent, Intent.ASK_SECURITY_QUESTION)
        self.assertGreaterEqual(conf, 50)

    def test_need_assistance(self):
        intent, conf = detect_user_intent("Help me recover my WhatsApp account")
        self.assertEqual(intent, Intent.RECOVERY_REQUEST)
        self.assertGreater(conf, 50)

    def test_safety_tips(self):
        intent, conf = detect_user_intent("How do I stay safe online?")
        self.assertIn(intent, (Intent.SAFETY_TIPS, Intent.ASK_SECURITY_QUESTION))
        self.assertGreater(conf, 0)


if __name__ == "__main__":
    unittest.main()
