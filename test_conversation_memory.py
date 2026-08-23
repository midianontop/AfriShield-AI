import unittest
from conversation_memory import memory, ConversationMemory
from datetime import datetime


class ConversationMemoryTests(unittest.TestCase):
    def setUp(self):
        # ensure clean slate
        memory.clear("user-123")

    def test_add_and_summary_merge_entities(self):
        analysis1 = {
            "entities": {"amounts": [20000], "banks": ["GTBank"]},
            "user_intent": "REPORT_INCIDENT",
            "intent_confidence": 86.0,
            "severity": type("S", (), {"rank": 2}),
            "confidence": 88.2,
        }
        analysis2 = {
            "entities": {"amounts": [5000], "otp_codes_or_mentions": True},
            "user_intent": "REPORT_INCIDENT",
            "intent_confidence": 90.0,
            "severity": type("S", (), {"rank": 3}),
            "confidence": 92.1,
        }

        memory.add_message("user-123", "Someone withdrew ₦20000 from my account", analysis1)
        memory.add_message("user-123", "I received an OTP and then money left", analysis2)

        summary = memory.get_incident_summary("user-123")
        self.assertIsNotNone(summary)
        # merged entities should include both amounts and bank
        self.assertIn("amounts", summary.merged_entities)
        self.assertIn(20000, summary.merged_entities["amounts"])
        self.assertIn(5000, summary.merged_entities["amounts"])
        self.assertIn("banks", summary.merged_entities)
        self.assertEqual(summary.last_intent, "REPORT_INCIDENT")
        self.assertGreaterEqual(summary.last_intent_confidence, 90.0)
        self.assertEqual(summary.max_severity_rank, 3)
        self.assertAlmostEqual(summary.max_confidence, 92.1)

    def test_clear_and_list_users(self):
        memory.add_message("u1", "hello", {})
        memory.add_message("u2", "hi", {})
        users = memory.list_users()
        self.assertIn("u1", users)
        self.assertIn("u2", users)
        memory.clear("u1")
        users2 = memory.list_users()
        self.assertNotIn("u1", users2)


if __name__ == "__main__":
    unittest.main()
