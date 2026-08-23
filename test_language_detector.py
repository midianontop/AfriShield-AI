import unittest

from language_detector import get_detector


class LanguageDetectorTests(unittest.TestCase):
    def test_detects_french_password_phrase(self):
        detector = get_detector()
        result = detector.detect("mot de passe")
        self.assertEqual(result.detected_language, "french")
        self.assertTrue(result.is_confident)

    def test_detects_accented_and_punctuated_text(self):
        detector = get_detector()
        result = detector.detect("Numéro de téléphone")
        self.assertEqual(result.detected_language, "french")
        self.assertTrue(result.is_confident)

    def test_treats_plain_english_as_unknown(self):
        detector = get_detector()
        result = detector.detect("someone stole money from my bank account")
        self.assertEqual(result.detected_language, "unknown")
        self.assertFalse(result.is_confident)


if __name__ == "__main__":
    unittest.main()
