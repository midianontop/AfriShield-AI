import unittest

from entity_extractor import extract_entities


class EntityExtractionTests(unittest.TestCase):
    def test_bank_and_amount_and_otp(self):
        text = "My GTBank account was hacked and they took ₦5,000. Someone asked for my OTP 123456"
        ents = extract_entities(text)
        self.assertIn("GTBank", " ".join(ents.get("banks", [])))
        self.assertTrue(any(a for a in ents.get("amounts", []) if "5000" in a.replace(',', '')))
        self.assertIn("123456", " ".join(ents.get("otp_codes_or_mentions", [])))
        self.assertGreaterEqual(ents.get("severity_hint", 0), 70)

    def test_device_theft(self):
        text = "My phone was stolen yesterday"
        ents = extract_entities(text)
        self.assertIn("phone", " ".join(ents.get("devices", [])).lower())
        self.assertIn("yesterday", " ".join(ents.get("times", [])).lower())
        self.assertGreaterEqual(ents.get("severity_hint", 0), 20)


if __name__ == "__main__":
    unittest.main()
