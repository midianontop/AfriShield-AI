import unittest

from app import build_incident_summary, build_intent_explanation


class AppExplanationTests(unittest.TestCase):
    def test_build_incident_summary_includes_key_details(self):
        summary = build_incident_summary("Phishing Attack", "🟠 High", 87.0, ["otp", "login link"])

        self.assertIn("Incident Summary", summary)
        self.assertIn("Phishing Attack", summary)
        self.assertIn("High", summary)
        self.assertIn("87%", summary)
        self.assertIn("otp", summary)

    def test_build_intent_explanation_mentions_reason(self):
        explanation = build_intent_explanation(
            "Report Incident",
            88.0,
            ["my account", "hacked"],
            question=False,
        )

        self.assertIn("Detected Intent", explanation)
        self.assertIn("Report Incident", explanation)
        self.assertIn("my account", explanation)
        self.assertIn("hacked", explanation)


if __name__ == "__main__":
    unittest.main()
