"""
================================================================================
  AfriShield AI
  Translation Engine
================================================================================

  Loads per-language glossary files from a folder and translates recognized
  security/fraud vocabulary into canonical English keywords, so the rest of
  the detection pipeline can match on a single language.

  Supports two glossary schemas, transparently:
    - Simple flat   : {"phrase": "english equivalent", ...}
    - Rich (v2+)    : {"_metadata": {...}, "stopwords": {...}, "categories": {...},
                       "translations": {"phrase": {"english": "...",
                                                     "confidence": "...",
                                                     "note": "..."}, ...}}
  Both are normalized internally into the same lookup table, so callers
  don't need to know or care which schema a given language file uses.

  Author  : Midian
  Module  : translations.py
  Version : 2.0.0
================================================================================
"""

from __future__ import annotations

import json
import logging
import re
import unicodedata
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Tuple

logger = logging.getLogger("afrishield_ai.translations")

DEFAULT_LANGUAGE_FOLDER = "languages"
ENGLISH = "english"

_RESERVED_KEYS = {"_metadata", "stopwords", "categories", "translations", "phrases"}


# ==============================================================================
# RESULT TYPES
# ==============================================================================

@dataclass
class TranslationMatch:
    phrase: str
    english: str
    confidence: str = "unknown"


@dataclass
class TranslationResult:
    original_text: str
    translated_text: str
    language: str
    matches: list[TranslationMatch] = field(default_factory=list)

    @property
    def matched(self) -> bool:
        return bool(self.matches)


# ==============================================================================
# SCHEMA NORMALIZATION
# ==============================================================================

def _normalize_text(value: Any) -> str:
    """Normalize a phrase or input string for robust matching across accents,
    punctuation, spacing, and common Hausa ASCII spellings.
    """
    if value is None:
        return ""
    text = str(value).lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("ɓ", "b").replace("Ɓ", "b")
    text = text.replace("ɗ", "d").replace("Ɗ", "d")
    text = text.replace("ƙ", "k").replace("Ƙ", "k")
    text = re.sub(r"[^\w]+", " ", text, flags=re.UNICODE).strip()
    return text


def _normalize_entry(value: Any) -> tuple[str, str] | None:
    """
    Normalize one glossary entry into (english, confidence).
    Accepts a plain string ("english equivalent") for the simple flat
    schema, or a dict ({"english": ..., "confidence": ...}) for the rich
    schema. Returns None for blank/placeholder entries, which are skipped.
    """
    if isinstance(value, str):
        value = value.strip()
        return (value, "unknown") if value else None
    if isinstance(value, dict):
        english = str(value.get("english", "")).strip()
        if not english:
            return None
        return english, str(value.get("confidence", "unknown"))
    return None


def _extract_glossary(raw: dict[str, Any]) -> dict[str, tuple[str, str]]:
    """
    Given a parsed language JSON file (either schema), return a flat
    {phrase: (english, confidence)} lookup table, skipping the rich
    schema's metadata/stopwords/categories keys.

    The glossary can be sourced from both the traditional "translations"
    mapping and the newer top-level "phrases" mapping.
    """
    sources: list[dict[str, Any]] = []

    translations_source = raw.get("translations")
    if isinstance(translations_source, dict):
        sources.append(translations_source)

    phrases_source = raw.get("phrases")
    if isinstance(phrases_source, dict):
        sources.append(phrases_source)

    if not sources:
        fallback_source = raw.get("translations", raw)
        if isinstance(fallback_source, dict):
            sources.append(fallback_source)
        else:
            return {}

    glossary: dict[str, tuple[str, str]] = {}
    for source in sources:
        for phrase, value in source.items():
            if phrase in _RESERVED_KEYS:
                continue
            normalized = _normalize_entry(value)
            if normalized is not None:
                normalized_phrase = _normalize_text(phrase)
                if normalized_phrase:
                    glossary[normalized_phrase] = normalized
    return glossary


def _extract_stopwords(raw: dict[str, Any]) -> set[str]:
    stopwords = raw.get("stopwords", {})
    if isinstance(stopwords, dict):
        normalized_words = {_normalize_text(w) for w in stopwords.keys()}
        return {w for w in normalized_words if w}
    if isinstance(stopwords, list):
        normalized_words = {_normalize_text(str(w)) for w in stopwords}
        return {w for w in normalized_words if w}
    return set()


# ==============================================================================
# TRANSLATOR
# ==============================================================================

class Translator:
    """
    Loads every *.json glossary file from `language_folder` (one file per
    language; filename without extension = language name, e.g. hausa.json
    -> "hausa") and translates recognized phrases into English.

    It also supports reverse translation for a small subset of common terms,
    which is useful when the app needs to respond in the user's original
    language after analysis in English.
    """

    def __init__(self, language_folder: str = DEFAULT_LANGUAGE_FOLDER):
        self.language_folder = language_folder
        self.languages: dict[str, dict[str, tuple[str, str]]] = {}
        self.stopwords: dict[str, set[str]] = {}
        # Per-language compiled matchers for forward translation
        self._patterns: dict[str, re.Pattern[str]] = {}
        # Per-language cached reverse translation patterns: list of
        # (compiled_pattern, target_phrase) for english->local replacements
        self._reverse_patterns: dict[str, List[Tuple[re.Pattern[str], str]]] = {}
        self.load_languages()

    def load_languages(self) -> None:
        """(Re)scan the language folder and rebuild all lookup tables.
        Never raises: a missing folder, an unreadable file, or malformed
        JSON in one language simply skips that language (with a logged
        warning) instead of taking down the whole translator."""
        self.languages.clear()
        self.stopwords.clear()
        self._patterns.clear()
        self._reverse_patterns.clear()

        folder = Path(self.language_folder)
        if not folder.is_dir():
            logger.warning("Language folder '%s' does not exist; no languages loaded.", folder)
            return

        for file_path in sorted(folder.glob("*.json")):
            language_name = file_path.stem.lower()
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                if not content.strip():
                    raw = {}
                else:
                    raw = json.loads(content)
            except (OSError, json.JSONDecodeError) as exc:
                logger.error("Failed to load language file '%s': %s", file_path, exc)
                continue

            if not isinstance(raw, dict):
                logger.error("Language file '%s' must contain a JSON object; skipping.", file_path)
                continue

            glossary = _extract_glossary(raw)
            self.languages[language_name] = glossary
            self.stopwords[language_name] = _extract_stopwords(raw)
            self._patterns[language_name] = self._build_pattern(glossary)
            logger.info("Loaded %d term(s) for language '%s'.", len(glossary), language_name)

        if ENGLISH not in self.languages:
            self.languages[ENGLISH] = {}
            self.stopwords[ENGLISH] = set()
            self._patterns[ENGLISH] = None

    reload = load_languages  # explicit, discoverable alias

    @staticmethod
    def _build_pattern(glossary: dict[str, tuple[str, str]]) -> re.Pattern[str] | None:
        """Compile one alternation regex per language (longest phrases
        first, so multi-word phrases win over their component words),
        instead of N sequential naive .replace() calls. Word-boundaried
        so e.g. a key 'an' can never clobber part of 'banki'."""
        if not glossary:
            return None
        phrases = sorted(glossary.keys(), key=lambda p: (-len(p), p))
        escaped = [re.escape(p) for p in phrases]
        try:
            return re.compile(r"(?<!\w)(" + "|".join(escaped) + r")(?!\w)", flags=re.UNICODE)
        except re.error as exc:
            logger.error("Failed to compile matcher pattern: %s", exc)
            return None

    @staticmethod
    def _build_reverse_patterns(glossary: dict[str, tuple[str, str]]) -> List[Tuple[re.Pattern[str], str]]:
        """Build compiled regex patterns to translate English terms back into
        the target language. Returns a list of (pattern, target_phrase),
        ordered so longer English phrases are replaced first.
        """
        reverse_entries: List[Tuple[str, str]] = []
        for phrase, (english, _) in glossary.items():
            english_term = english.lower().strip()
            if english_term:
                reverse_entries.append((
                    _normalize_text(english_term),
                    phrase,
                ))

        if not reverse_entries:
            return []

        # Longer English phrases first to avoid partial matches
        reverse_entries.sort(key=lambda item: len(item[0].split()), reverse=True)

        compiled: List[Tuple[re.Pattern[str], str]] = []
        for eng, target in reverse_entries:
            try:
                pat = re.compile(r"(?<!\w)" + re.escape(eng) + r"(?!\w)", flags=re.UNICODE)
            except re.error:
                continue
            compiled.append((pat, target))
        return compiled

    def available_languages(self) -> list[str]:
        return sorted(self.languages.keys())

    def is_supported(self, language: str) -> bool:
        language = language.lower()
        return language == ENGLISH or language in self.languages

    def translate(self, text: str, language: str) -> str:
        """Backward-compatible simple API — returns the translated string."""
        return self.translate_detailed(text, language).translated_text

    def translate_to_language(self, text: str, language: str) -> str:
        """Translate English text back into the target language when possible."""
        language = language.lower()
        if language in {ENGLISH, ""}:
            return text

        glossary = self.languages.get(language)
        if not glossary:
            return text

        if not text or not str(text).strip():
            return text

        normalized_text = _normalize_text(text)
        if not normalized_text:
            return text

        reverse_patterns = self._reverse_patterns.get(language) or []
        if not reverse_patterns:
            return text

        translated_text = normalized_text
        for pattern, target_phrase in reverse_patterns:
            translated_text = pattern.sub(target_phrase, translated_text)

        return translated_text

    def translate_detailed(self, text: str, language: str) -> TranslationResult:
        """
        Full API: returns a TranslationResult with the translated text AND
        the list of matched phrases, each with its English equivalent and
        confidence level — so callers can, for example, treat "verified"
        matches differently from "community"/"uncertain" ones.
        """
        language = language.lower()
        if language == ENGLISH:
            return TranslationResult(original_text=text, translated_text=text, language=language)

        glossary = self.languages.get(language)
        pattern = self._patterns.get(language)
        if not glossary or pattern is None:
            logger.debug("No glossary loaded for language '%s'; returning text unchanged.", language)
            return TranslationResult(original_text=text, translated_text=text, language=language)

        matches: list[TranslationMatch] = []
        normalized_text = _normalize_text(text)

        if normalized_text in glossary:
            english, confidence = glossary[normalized_text]
            matches.append(TranslationMatch(phrase=normalized_text, english=english, confidence=confidence))
            return TranslationResult(
                original_text=text,
                translated_text=english,
                language=language,
                matches=matches,
            )

        def _replace(m: re.Match[str]) -> str:
            phrase = m.group(0)
            english, confidence = glossary[phrase]
            matches.append(TranslationMatch(phrase=phrase, english=english, confidence=confidence))
            return english

        translated = pattern.sub(_replace, normalized_text)
        return TranslationResult(
            original_text=text, translated_text=translated, language=language, matches=matches
        )

    def translate_message(self, text: str, language: str | None = None) -> dict[str, Any]:
        """Detect a language if needed and translate the input into canonical English.

        The returned dictionary is intentionally simple for downstream callers.
        """
        if not text or not str(text).strip():
            return {
                "original": text,
                "language": "unknown",
                "translated": "",
                "matched_phrases": [],
            }

        normalized_language = language.lower().strip() if language else ""
        detection_result = None

        if not normalized_language or normalized_language == "unknown":
            try:
                from language_detector import detect_language_detailed

                detection_result = detect_language_detailed(text)
                normalized_language = detection_result.detected_language
            except Exception:
                normalized_language = "unknown"

        if normalized_language in {"", "unknown"}:
            return {
                "original": text,
                "language": "unknown",
                "translated": text,
                "matched_phrases": [],
            }

        translation_result = self.translate_detailed(text, normalized_language)
        result = {
            "original": text,
            "language": translation_result.language,
            "translated": translation_result.translated_text,
            "matched_phrases": [match.phrase for match in translation_result.matches],
        }

        if detection_result is not None:
            result["confidence"] = detection_result.confidence
            result["ambiguous"] = detection_result.ambiguous

        return result

    def strip_stopwords(self, text: str, language: str) -> str:
        """Remove known grammatical filler words for a language (e.g.
        Hausa 'an', 'yi', 'ne') before matching, using the glossary's
        stopword list if the language file provided one."""
        stopword_set = self.stopwords.get(language.lower(), set())
        if not stopword_set:
            return text
        tokens = _normalize_text(text).split()
        return " ".join(t for t in tokens if t not in stopword_set)


# ==============================================================================
# MODULE-LEVEL SINGLETON
# ==============================================================================

_translator_instance: Translator | None = None


def get_translator(language_folder: str = DEFAULT_LANGUAGE_FOLDER) -> Translator:
    """Lazily-created, cached singleton — the preferred way to obtain a
    Translator (easier to test/reconfigure than relying on import-time
    side effects)."""
    global _translator_instance
    if _translator_instance is None:
        _translator_instance = Translator(language_folder)
    return _translator_instance

# Backward-compatible module-level instance: lazily-created on first use.
_translator_instance: Translator | None = None


@lru_cache(maxsize=1024)
def translate_message(text: str, language: str | None = None) -> dict[str, Any]:
    """Convenience wrapper over the shared Translator instance."""
    return get_translator().translate_message(text, language)


# ==============================================================================
# CLI SELF-TEST
# ==============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    translator = get_translator(DEFAULT_LANGUAGE_FOLDER)
    print("Available languages:", translator.available_languages() or "(none found)")
    for lang in translator.available_languages():
        sample = next(iter(translator.languages[lang]), None)
        if sample:
            result = translator.translate_detailed(sample, lang)
            print(f"  [{lang}] {sample!r} -> {result.translated_text!r} "
                  f"({len(result.matches)} match(es))")