"""Tests for the config module."""

import os
import tempfile
from pathlib import Path

from kairos.core.config import (
    KairosConfig,
    get_default_config,
    load_config,
    resolve_journal_path,
)


class TestKairosConfig:
    """Tests for KairosConfig model."""

    def test_defaults_have_demo_mode_true(self):
        """Default config should have demo_mode=True."""
        config = KairosConfig()
        assert config.demo_mode is True

    def test_defaults_have_empty_api_keys(self):
        """Default config should have empty api_keys dict."""
        config = KairosConfig()
        assert config.api_keys == {}

    def test_defaults_have_expected_data_settings(self):
        """Default config should have expected data_settings."""
        config = KairosConfig()
        assert config.data_settings["default_source"] == "mock"
        assert config.data_settings["cache_ttl_seconds"] == 300

    def test_defaults_have_expected_agent_params(self):
        """Default config should have expected agent_params."""
        config = KairosConfig()
        assert config.agent_params["default"]["confidence_threshold"] == 0.6
        assert config.agent_params["default"]["max_position_pct"] == 0.1


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_config_without_env_returns_valid_config(self):
        """load_config without .env file should return a valid config."""
        config = load_config()
        assert isinstance(config, KairosConfig)
        assert isinstance(config.demo_mode, bool)
        assert isinstance(config.api_keys, dict)

    def test_load_config_no_env_sets_demo_mode_true(self, monkeypatch):
        """Without any API keys, load_config should set demo_mode=True."""
        for key in ["BIRDEYE_API_KEY", "HELIUS_API_KEY", "COINGECKO_API_KEY"]:
            monkeypatch.delenv(key, raising=False)
        config = load_config()
        assert config.demo_mode is True

    def test_env_vars_populate_api_keys(self, monkeypatch):
        """Environment variables should populate api_keys dict."""
        monkeypatch.setenv("BIRDEYE_API_KEY", "test_birdeye_key")
        monkeypatch.setenv("HELIUS_API_KEY", "test_helius_key")

        config = load_config()

        assert "BIRDEYE_API_KEY" in config.api_keys
        assert config.api_keys["BIRDEYE_API_KEY"] == "test_birdeye_key"
        assert "HELIUS_API_KEY" in config.api_keys
        assert config.api_keys["HELIUS_API_KEY"] == "test_helius_key"

    def test_api_key_found_sets_demo_mode_false(self, monkeypatch):
        """When any API key is found, demo_mode should be False."""
        monkeypatch.setenv("COINGECKO_API_KEY", "test_coingecko_key")

        config = load_config()

        assert config.demo_mode is False

    def test_load_config_from_specific_path(self, monkeypatch):
        """load_config should load from a specific path when given."""
        monkeypatch.delenv("BIRDEYE_API_KEY", raising=False)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("COINGECKO_API_KEY=test_coingecko_key\n")
            env_path = f.name

        try:
            config = load_config(path=env_path)
            assert "COINGECKO_API_KEY" in config.api_keys
            assert config.api_keys["COINGECKO_API_KEY"] == "test_coingecko_key"
        finally:
            os.unlink(env_path)

    def test_load_config_missing_path_does_not_raise(self):
        """load_config with non-existent path should not raise."""
        config = load_config(path="/nonexistent/path/.env")
        assert isinstance(config, KairosConfig)


class TestGetDefaultConfig:
    """Tests for get_default_config function."""

    def test_returns_kairos_config_instance(self):
        """get_default_config should return KairosConfig instance."""
        config = get_default_config()
        assert isinstance(config, KairosConfig)

    def test_returns_factory_defaults(self):
        """get_default_config should return config with factory defaults."""
        config = get_default_config()
        assert config.demo_mode is True
        assert config.api_keys == {}


class TestResolveJournalPath:
    """Tests for resolve_journal_path function."""

    def test_returns_path_to_journal_json(self):
        """resolve_journal_path should return path ending with journal.json."""
        config = get_default_config()
        path = resolve_journal_path(config)
        assert path.name == "journal.json"

    def test_returns_expanded_home_path(self):
        """resolve_journal_path should expand ~ to home directory."""
        config = get_default_config()
        path = resolve_journal_path(config)
        assert str(path).startswith(os.fspath(Path.home()))

    def test_creates_parent_directory(self, tmp_path, monkeypatch):
        """resolve_journal_path should create parent directory if needed."""
        custom_path = tmp_path / ".kairos" / "journal.json"
        monkeypatch.setattr(Path, "expanduser", lambda self: custom_path)
        config = KairosConfig()
        path = resolve_journal_path(config)
        assert path.parent.exists()

    def test_honors_configured_journal_path(self, tmp_path):
        """A non-empty config.journal_path should be used verbatim."""
        target = tmp_path / "custom" / "my_journal.json"
        config = KairosConfig(journal_path=str(target))
        path = resolve_journal_path(config)
        assert path == target
        assert path.parent.exists()
