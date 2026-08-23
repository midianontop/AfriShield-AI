import unittest

from translations import get_translator, translate_message


class TranslationTests(unittest.TestCase):
    def test_loads_multiple_language_glossaries(self):
        translator = get_translator("languages")
        languages = set(translator.available_languages())

        for expected in ["english", "hausa", "swahili", "yoruba", "amharic", "zulu", "xhosa", "oromo", "french", "arabic"]:
            self.assertIn(expected, languages)

    def test_matches_punctuation_and_unicode_variants(self):
        translator = get_translator("languages")

        self.assertEqual(translator.translate("mot-de-passe", "french"), "password")
        self.assertEqual(translator.translate("numéro de téléphone", "french"), "phone number")

    def test_translates_english_terms_back_to_target_language(self):
        translator = get_translator("languages")

        self.assertEqual(translator.translate_to_language("fraud", "arabic"), "احتيال")
        self.assertEqual(translator.translate_to_language("password", "arabic"), "كلمة مرور")
        self.assertEqual(translator.translate_to_language("phone number", "arabic"), "رقم الهاتف")

    def test_hausa_phrase_matching_and_normalization(self):
        translator = get_translator("languages")

        self.assertEqual(translator.translate("AN YI MIN ZAMBA!!", "hausa"), "i was scammed")
        self.assertEqual(translator.translate("sun nemi bvn dina", "hausa"), "they asked for my bvn")
        self.assertEqual(translator.translate("an hacke", "hausa"), "hacked")
        self.assertEqual(translator.translate("Na karbi sakon whatsapp na bogi", "hausa"), "i received a fake whatsapp message")

    def test_translate_message_detects_and_returns_matched_phrases(self):
        result = translate_message("An yi min zamba")

        self.assertEqual(result["original"], "An yi min zamba")
        self.assertEqual(result["language"], "hausa")
        self.assertEqual(result["translated"], "i was scammed")
        self.assertIn("an yi min zamba", result["matched_phrases"])
        self.assertGreaterEqual(result.get("confidence", 0), 0)


if __name__ == "__main__":
    unittest.main()
