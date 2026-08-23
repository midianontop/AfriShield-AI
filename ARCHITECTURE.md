# AfriShield AI Architecture

## Overview

AfriShield AI is organized into three main layers:

- **Language Layer** — handles language detection, translation, and phrase matching.
- **Intelligence Layer** — performs intent detection, threat classification, entity extraction, severity/confidence scoring, and conversation memory.
- **Knowledge Layer** — stores and retrieves cybersecurity content for RAG-enhanced responses.

```
                 AfriShield AI
                        │
        ┌───────────────┼────────────────┐
        │               │                │
 Language Layer     Intelligence      Knowledge Layer
        │               │                │
        ▼               ▼                ▼
 Language Detector   Intent Detection   RAG Knowledge Base
 Translation Engine  Threat Detector    Cybersecurity PDFs
 Phrase Matching     Scam Detector      Incident Guides
 Response Language   Entity Extraction  OWASP
                     Severity Engine
                     Confidence Engine
                     Explainable AI
                     Conversation Memory
```

## Current Module Mapping

### Language Layer

- `language_detector.py`
  - Detects the incoming language based on glossary matches and stopwords.
- `translations.py`
  - Loads JSON glossaries from `languages/`, normalizes the schema, and supports translation.
- `languages/`
  - Contains language-specific phrase mappings and glossary data.

### Intelligence Layer

- `threat_detector.py`
  - Core threat classification engine.
  - Uses fuzzy phrase matching and keyword weights to classify incidents.
  - Computes severity and confidence.
  - Distinguishes active incident reports from general security questions.
  - Now supports `user_id`-aware in-memory persistence.
- `entity_extractor.py`
  - Extracts structured indicators such as banks, amounts, OTP references, emails, phone numbers, times, and devices.
  - Provides severity hints for concrete incident signals.
- `scam_detector.py`
  - Focused on scam-specific detection logic and fraud patterns.
- `threat_classifier.py`
  - Additional classification utilities used alongside the main threat detector.
- `confidence.py`
  - Contains scoring heuristics and confidence-related helpers.
- `conversation_memory.py`
  - In-memory incident memory store.
  - Aggregates messages, merged entities, highest-severity state, and intent confidence per user.
- `incident_response.py`
  - Maps categories to remediation guidance and response templates.

### Knowledge Layer

- `full_rag.py`
  - Connects retrieval and generation for RAG-enhanced responses.
- `retriever.py`
  - Handles document retrieval from vector stores or local data.
- `rag_chat.py`
  - Manages chat-style RAG interaction.
- `generate_answer.py`
  - Builds response text from retrieved references and the detected threat.
- `create_embeddings.py`, `build_vector_db.py`, `search_vector_db.py`
  - Manage vector database creation and searching.
- `documents/`
  - Stores source cybersecurity text and guides used for retrieval.
- `vector_db/`
  - Contains serialized document embeddings and index data.

## Data Flow

1. User text enters the system.
2. The language layer determines language and normalizes phrases.
3. The intelligence layer analyzes the text:
   - Detects user intent and incident type.
   - Extracts entities and calculates severity/confidence.
   - Classifies the threat category.
   - Persists the result to conversation memory when a `user_id` is supplied.
4. The knowledge layer retrieves relevant references and generates an explainable response.

## Notes

- The architecture is designed for offline operation, minimizing external dependencies.
- The current design supports extending the RAG layer to a real LLM or richer vector store without changing the core detector.
- The conversation memory module is intentionally lightweight and in-memory.

## Suggested Next Improvements

- Add a persisted memory backend for sessions that outlive the process.
- Integrate more localized glossaries into intent detection.
- Add an explicit `Explainable AI` module for rule-based reasoning traces.
- Expand the RAG knowledge base with additional incident response guides.
