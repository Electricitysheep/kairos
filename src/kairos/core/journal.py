"""Decision Journal module for Kairos trading agents."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class JournalEntry(BaseModel):
    """A single decision entry in the trading journal."""

    timestamp: str = Field(default="")
    token: str = Field(default="")
    decision: str = Field(default="HOLD")
    confidence: float = Field(default=0.0)
    reasoning_summary: str = Field(default="")
    data_sources: list[str] = Field(default_factory=list)
    research_agent: dict = Field(default_factory=dict)
    quant_agent: dict = Field(default_factory=dict)
    risk_agent: dict = Field(default_factory=dict)
    final_action: dict = Field(default_factory=dict)

    @model_validator(mode="after")
    def _set_default_timestamp(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        return self


class DecisionJournal:
    """A journal that records and retrieves agent decisions."""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path
        self.entries: list[JournalEntry] = []
        if self.storage_path:
            path = Path(self.storage_path)
            if path.exists():
                raw = path.read_text(encoding="utf-8")
                if raw.strip():
                    data = json.loads(raw)
                    self.entries = [JournalEntry(**item) for item in data]

    def append(self, entry: JournalEntry) -> None:
        """Add a journal entry."""
        self.entries.append(entry)

    def get_all(self) -> list[JournalEntry]:
        """Return all journal entries."""
        return list(self.entries)

    def get_latest(self, n: int = 10) -> list[JournalEntry]:
        """Return the n most recent entries."""
        return list(self.entries[-n:])

    def export_json(self, path: str) -> None:
        """Write all entries to a JSON file."""
        data = [entry.model_dump() for entry in self.entries]
        Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load_json(cls, path: str) -> "DecisionJournal":
        """Load entries from a JSON file and return a new DecisionJournal."""
        raw = Path(path).read_text(encoding="utf-8")
        data = json.loads(raw)
        instance = cls()
        instance.entries = [JournalEntry(**item) for item in data]
        return instance

    def clear(self) -> None:
        """Remove all journal entries."""
        self.entries.clear()
