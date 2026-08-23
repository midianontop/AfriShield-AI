"""
================================================================================
  AfriShield AI
  Conversation Memory
================================================================================

  Lightweight, thread-safe, in-memory session history per user. Lets
  threat_detector.py (and other callers) look back at a user's recent
  messages within a session.

  This is intentionally NOT persistent storage: it lives only for the
  lifetime of the running process, and is capped per-user so a long-running
  server doesn't grow memory unboundedly for one chatty or abusive session.
  For real persistence across restarts, swap ConversationMemory's internal
  store for a database-backed implementation — the public interface
  (add_message / get_history / get_recent / clear) would not need to change.

  Known gap (not fixed here, since it's a threat_detector.py change, not
  this module's): the metadata dict threat_detector.py currently passes to
  add_message() includes severity/confidence/entities/intent, but NOT the
  matched threat category — so category-level recurrence tracking (e.g.
  "this user has now reported 3 separate Financial Fraud incidents this
  session") isn't possible yet from this data alone. severity_recurrence()
  below works with what's actually available today.

  Author  : Midian
  Module  : conversation_memory.py
  Version : 1.0.0
================================================================================
"""

from __future__ import annotations

import threading
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

# Cap how many messages are kept per user so memory usage stays bounded
# regardless of how long a session runs.
MAX_HISTORY_PER_USER = 50


@dataclass
class MemoryEntry:
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ConversationMemory:
    """Thread-safe, in-memory, per-user rolling message history."""

    def __init__(self, max_history_per_user: int = MAX_HISTORY_PER_USER):
        self._max_history = max_history_per_user
        self._store: dict[str, deque[MemoryEntry]] = defaultdict(
            lambda: deque(maxlen=self._max_history)
        )
        self._lock = threading.Lock()

    def add_message(self, user_id: str, text: str, metadata: dict[str, Any] | None = None) -> None:
        """Record one message plus its analysis metadata for a user.
        Silently no-ops on an empty user_id rather than raising, since
        callers may pass an optional/absent id."""
        if not user_id:
            return
        entry = MemoryEntry(text=text, metadata=metadata or {})
        with self._lock:
            self._store[user_id].append(entry)

    def get_history(self, user_id: str) -> list[MemoryEntry]:
        """Full retained history for a user, oldest first."""
        with self._lock:
            return list(self._store.get(user_id, []))

    def get_recent(self, user_id: str, n: int = 5) -> list[MemoryEntry]:
        """Last n entries for a user, oldest first."""
        with self._lock:
            history = list(self._store.get(user_id, []))
        return history[-n:]

    def clear(self, user_id: str) -> None:
        with self._lock:
            self._store.pop(user_id, None)

    def clear_all(self) -> None:
        with self._lock:
            self._store.clear()

    def severity_recurrence(self, user_id: str, window: int = 10) -> dict[str, int]:
        """
        Count how many of a user's last `window` messages were tagged at
        each severity level. A simple building block for session-level
        escalation: repeated High/Critical reports in one session are a
        stronger signal than any single message alone, even before
        category-level tracking (see the module docstring's noted gap)
        is available.
        """
        with self._lock:
            recent = list(self._store.get(user_id, []))[-window:]
        counts: dict[str, int] = {}
        for entry in recent:
            severity = entry.metadata.get("severity")
            label = getattr(severity, "value", severity)  # tolerate Severity enum or plain string
            if label:
                counts[label] = counts.get(label, 0) + 1
        return counts


# Module-level singleton, matching how threat_detector.py imports it:
#     from conversation_memory import memory as conversation_memory
memory = ConversationMemory()


if __name__ == "__main__":
    memory.add_message("user_1", "my account was hacked", {"severity": "🟠 High", "confidence": 80})
    memory.add_message("user_1", "they also asked for my otp", {"severity": "🟠 High", "confidence": 85})
    memory.add_message("user_1", "what is phishing?", {"severity": "🟢 Low", "confidence": 0})

    print("Full history:")
    for e in memory.get_history("user_1"):
        print(" ", e.text, "->", e.metadata)

    print("Recent 2:", [e.text for e in memory.get_recent("user_1", 2)])
    print("Severity recurrence:", memory.severity_recurrence("user_1"))