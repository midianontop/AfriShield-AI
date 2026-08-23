"""
================================================================================
  AfriShield AI
  Language Detector
================================================================================

  Detects which language a piece of user text is most likely written in, by
  scoring it against every glossary the Translation Engine (translations.py)
  already has loaded — the same hausa.json / igbo.json / swahili.json /
  yoruba.json files — so there is exactly one place each language's
  vocabulary lives, instead of a second, hand-maintained keyword list that
  drifts out of sync with it.

  Why not the original hardcoded LANGUAGE_KEYWORDS dict?
    - It listed only 6-8 words per language — a tiny, stale fraction of the
      50-70+ terms each glossary file actually has now.
    - It omitted Yoruba entirely, even though yoruba.json exists and is
      loaded everywhere else in the project.
    - It had no detection function at all — just the keyword data sitting
      there, with no logic that ever used it.
    - The obvious next step, naive substring counting, would reproduce
      every bug already found and fixed in translations.py: no word
      boundaries (so a short key like "an" would match inside an unrelated
      word), and no handling for Unicode combining marks (Yoruba tone
      marks like "ọ́" silently fail to match at all with a plain regex \\b).

  This version reuses Translator's already-compiled, already-fixed matching
  patterns and stopword lists directly, so both problems are solved for
  free and stay solved as the glossaries grow.

  Author  : Midian
  Module  : language_detector.py
  Version : 2.0.0
================================================================================
"""

from __future__ import annotations

import logging
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field

from translations import ENGLISH, Translator, get_translator

logger = logging.getLogger("afrishield_ai.language_detector")

# Content-glossary matches (security/fraud vocabulary, e.g. "banki", "kudi")
# are highly language-specific but relatively rare in a short message.
# Stopword matches (grammatical function words, e.g. "na", "ti") are less
# specific individually — several overlap across languages — but appear
# far more often in ordinary sentences. These weights are a reasonable
# starting point, not a tuned model; see the module docstring's note on
# known limitations below and check_stopword_overlap() for where cross-
# language collisions actually come from.
GLOSSARY_MATCH_WEIGHT = 3
STOPWORD_MATCH_WEIGHT = 1

# Below this combined score, we report "unknown" rather than guessing a
# language with unjustified confidence.
MIN_CONFIDENT_SCORE = 3

# If the runner-up's score is at least this fraction of the top score,
# the result is flagged ambiguous rather than reported with false
# confidence (e.g. text using only cross-language stopwords).
AMBIGUITY_RATIO = 0.8

# Glossary matches carry more weight than stopwords. The exact numeric
# values are intentionally simple, but they help prefer a verified fraud
# phrase over a generic grammatical token like "na" or "ko".
CONFIDENCE_WEIGHTS = {
    "verified": 3,
    "common": 2,
    "uncertain": 1,
    "unknown": 1,
}


# ==============================================================================
# RESULT TYPES
# ==============================================================================

@dataclass
class LanguageScore:
    language: str
    score: float
    glossary_matches: list[str] = field(default_factory=list)
    stopword_matches: list[str] = field(default_factory=list)


@dataclass
class DetectionResult:
    text: str
    detected_language: str
    confidence: float
    scores: list[LanguageScore] = field(default_factory=list)
    ambiguous: bool = False

    @property
    def is_confident(self) -> bool:
        return self.detected_language != "unknown" and not self.ambiguous


# ==============================================================================
# DETECTOR
# ==============================================================================

class LanguageDetector:
    """
    Scores input text against every non-English language the shared
    Translator has loaded, using the SAME word-boundary-safe, Unicode-
    combining-mark-safe matching the translation engine itself relies on.
    """

    def __init__(self, translator: Translator | None = None):
        self.translator = translator or get_translator()

    @staticmethod
    def _normalize_text(text: str) -> str:
        if not text:
            return ""
        normalized = unicodedata.normalize("NFKD", text.lower())
        normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
        normalized = re.sub(r"[^\w]+", " ", normalized, flags=re.UNICODE).strip()
        return normalized

    def detect(self, text: str) -> DetectionResult:
        if not text or not text.strip():
            return DetectionResult(text=text, detected_language="unknown", confidence=0.0)

        normalized_text = self._normalize_text(text)
        candidate_languages = [
            lang for lang in self.translator.available_languages() if lang != ENGLISH
        ]
        tokens = normalized_text.split()

        scores: list[LanguageScore] = []
        for language in candidate_languages:
            result = self.translator.translate_detailed(text, language)
            glossary_matches = [m.phrase for m in result.matches]

            if not glossary_matches:
                # A language should generally have at least one security/fraud
                # term present before we consider it a strong candidate.
                continue

            glossary_score = sum(
                CONFIDENCE_WEIGHTS.get(m.confidence.lower(), 1)
                for m in result.matches
            )
            stopword_set = self.translator.stopwords.get(language, set())
            stopword_matches = [t for t in tokens if t in stopword_set]

            score = glossary_score * GLOSSARY_MATCH_WEIGHT
            score += len(stopword_matches) * STOPWORD_MATCH_WEIGHT

            scores.append(LanguageScore(
                language=language,
                score=score,
                glossary_matches=glossary_matches,
                stopword_matches=stopword_matches,
            ))

        scores.sort(key=lambda s: s.score, reverse=True)

        if not scores:
            return DetectionResult(text=text, detected_language="unknown", confidence=0.0, scores=scores)

        top = scores[0]
        total_score = sum(s.score for s in scores) or 1
        confidence = round((top.score / total_score) * 100, 1)
        ambiguous = len(scores) > 1 and scores[1].score >= top.score * AMBIGUITY_RATIO

        # English-like text often matches a few generic glossary entries across
        # many language files, but these should not be treated as strong
        # evidence for a specific language. Require a stronger margin before
        # committing to a non-English language.
        if top.score < MIN_CONFIDENT_SCORE * 2:
            ambiguous = True

        # Require a stronger signal before committing to a specific language.
        # Generic single-word matches like "money", "bank", and "account"
        # are too weak on their own, while longer multi-word phrases or
        # stopword-supported phrases are more meaningful.
        has_multiword_match = any(" " in phrase for phrase in top.glossary_matches)
        has_stopword_support = bool(top.stopword_matches)

        if not (has_multiword_match or has_stopword_support):
            return DetectionResult(text=text, detected_language="unknown", confidence=0.0, scores=scores)

        return DetectionResult(
            text=text,
            detected_language=top.language,
            confidence=confidence,
            scores=scores,
            ambiguous=ambiguous,
        )

    def check_stopword_overlap(self) -> dict[str, list[str]]:
        """
        Returns {stopword: [languages sharing it]} for every grammatical
        function word that appears in 2+ loaded languages' stopword lists.
        These are exactly the words that make short, low-content text
        ambiguous to detect — e.g. 'na' means 'and/with/at' in Igbo AND
        'and/with/by' in Swahili; matching on it alone tells you nothing.
        Mirrors Translator.check_category_consistency()'s role of
        surfacing real cross-file inconsistencies instead of hiding them.
        """
        word_to_langs: dict[str, list[str]] = defaultdict(list)
        for lang, stopword_set in self.translator.stopwords.items():
            if lang == ENGLISH:
                continue
            for word in stopword_set:
                word_to_langs[word].append(lang)
        return {w: sorted(langs) for w, langs in word_to_langs.items() if len(langs) > 1}


# ==============================================================================
# MODULE-LEVEL SINGLETON
# ==============================================================================

_detector_instance: LanguageDetector | None = None


def get_detector() -> LanguageDetector:
    """Lazily-created, cached singleton — mirrors translations.get_translator()."""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = LanguageDetector()
    return _detector_instance


def detect_language(text: str) -> str:
    """Simple API: just the detected language name ('hausa', 'unknown', etc.)."""
    return get_detector().detect(text).detected_language


def detect_language_detailed(text: str) -> DetectionResult:
    """Full API: complete DetectionResult with per-language scores,
    confidence, and an ambiguity flag for close calls."""
    return get_detector().detect(text)


# ==============================================================================
# CLI SELF-TEST
# ==============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    detector = get_detector()
    print("Languages this detector can recognize:",
          [l for l in detector.translator.available_languages() if l != ENGLISH])
    print()

    samples = {
        "hausa": "kudi na daga banki an sata",
        "yoruba": "olè ji owo lati ilé-ifowó-pamọ́",
        "igbo": "ha ezuru ego m na ụlọ akụ",
        "swahili": "pesa yangu imeibiwa na benki",
        "english (should be unknown)": "someone stole money from my bank account",
    }
    for expected, text in samples.items():
        result = detect_language_detailed(text)
        flag = " (AMBIGUOUS)" if result.ambiguous else ""
        print(f"  expected={expected:28s} -> detected={result.detected_language:8s} "
              f"confidence={result.confidence:5.1f}%{flag}")

    print()
    overlaps = detector.check_stopword_overlap()
    if overlaps:
        print(f"Stopword overlap check: {len(overlaps)} word(s) shared across 2+ languages:")
        for word, langs in sorted(overlaps.items()):
            print(f"  {word!r} -> {langs}")
    else:
        print("Stopword overlap check: no overlaps found.")