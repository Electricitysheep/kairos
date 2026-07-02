"""Tests for the DecisionJournal module."""

import tempfile
from pathlib import Path

from kairos.core.journal import DecisionJournal, JournalEntry


class TestJournalEntry:
    """Tests for JournalEntry model."""

    def test_create_entry_with_minimal_fields(self):
        """Entry should be created with defaults when only required fields given."""
        entry = JournalEntry()
        assert entry.token == ""
        assert entry.decision == "HOLD"
        assert entry.confidence == 0.0
        assert entry.reasoning_summary == ""
        assert entry.data_sources == []
        assert entry.research_agent == {}
        assert entry.quant_agent == {}
        assert entry.risk_agent == {}
        assert entry.final_action == {}

    def test_auto_timestamp(self):
        """Timestamp should be auto-set to current UTC ISO format."""
        entry = JournalEntry()
        assert entry.timestamp != ""
        # Verify it's a valid ISO format timestamp
        from datetime import datetime
        dt = datetime.fromisoformat(entry.timestamp)
        assert dt.tzinfo is not None  # Should have timezone info

    def test_custom_timestamp(self):
        """Explicit timestamp should be preserved."""
        entry = JournalEntry(timestamp="2024-01-15T10:30:00Z")
        assert entry.timestamp == "2024-01-15T10:30:00Z"

    def test_full_entry(self):
        """Entry with all fields should preserve values."""
        entry = JournalEntry(
            token="SOL-USDC",
            decision="BUY",
            confidence=0.85,
            reasoning_summary="Strong momentum signal",
            data_sources=["birdeye", "coingecko"],
            research_agent={"signal": "bullish"},
            quant_agent={"rsi": 32.5},
            risk_agent={"max_loss": "5%"},
            final_action={"type": "market_buy", "amount": 10.0},
        )
        assert entry.token == "SOL-USDC"
        assert entry.decision == "BUY"
        assert entry.confidence == 0.85
        assert entry.reasoning_summary == "Strong momentum signal"
        assert entry.data_sources == ["birdeye", "coingecko"]
        assert entry.research_agent == {"signal": "bullish"}
        assert entry.quant_agent == {"rsi": 32.5}
        assert entry.risk_agent == {"max_loss": "5%"}
        assert entry.final_action == {"type": "market_buy", "amount": 10.0}


class TestDecisionJournal:
    """Tests for DecisionJournal class."""

    def test_append_and_retrieve(self):
        """Entries appended should be retrievable via get_all()."""
        journal = DecisionJournal()
        entry1 = JournalEntry(token="SOL")
        entry2 = JournalEntry(token="BTC")
        journal.append(entry1)
        journal.append(entry2)
        entries = journal.get_all()
        assert len(entries) == 2
        assert entries[0].token == "SOL"
        assert entries[1].token == "BTC"

    def test_get_latest(self):
        """get_latest() should return the n most recent entries."""
        journal = DecisionJournal()
        for i in range(15):
            journal.append(JournalEntry(token=f"TOKEN{i}"))
        latest = journal.get_latest(n=5)
        assert len(latest) == 5
        assert latest[0].token == "TOKEN10"
        assert latest[4].token == "TOKEN14"

    def test_get_latest_default(self):
        """get_latest() should default to 10 entries."""
        journal = DecisionJournal()
        for i in range(12):
            journal.append(JournalEntry(token=f"TOKEN{i}"))
        latest = journal.get_latest()
        assert len(latest) == 10

    def test_export_and_import_json(self):
        """Export to JSON and reload should preserve all entries."""
        journal = DecisionJournal()
        journal.append(JournalEntry(token="AAA", decision="BUY", confidence=0.9))
        journal.append(JournalEntry(token="BBB", decision="SELL", confidence=0.7))

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            journal.export_json(temp_path)
            loaded = DecisionJournal.load_json(temp_path)
            assert len(loaded.get_all()) == 2
            assert loaded.get_all()[0].token == "AAA"
            assert loaded.get_all()[1].token == "BBB"
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_clear(self):
        """clear() should remove all entries."""
        journal = DecisionJournal()
        journal.append(JournalEntry(token="CLEAR"))
        journal.append(JournalEntry(token="TEST"))
        assert len(journal.get_all()) == 2
        journal.clear()
        assert len(journal.get_all()) == 0

    def test_load_existing_on_init(self):
        """Passing existing path to __init__ should load entries."""
        journal = DecisionJournal()
        journal.append(JournalEntry(token="INIT"))

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            journal.export_json(temp_path)
            loaded = DecisionJournal(storage_path=temp_path)
            assert len(loaded.get_all()) == 1
            assert loaded.get_all()[0].token == "INIT"
        finally:
            Path(temp_path).unlink(missing_ok=True)
