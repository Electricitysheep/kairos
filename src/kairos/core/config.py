"""Configuration module for Kairos."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel


class KairosConfig(BaseModel):
    """Kairos configuration model."""

    api_keys: dict[str, str] = {}
    demo_mode: bool = True
    data_settings: dict = {"default_source": "mock", "cache_ttl_seconds": 300}
    agent_params: dict = {"default": {"confidence_threshold": 0.6, "max_position_pct": 0.1}}
    journal_path: str = ""


def load_config(path: str | None = None) -> KairosConfig:
    """Load KairosConfig from .env file and environment variables.

    Args:
        path: Optional path to .env file. If not given, searches for .env
              in CWD then parent directories.

    Returns:
        KairosConfig instance populated from .env and environment.
    """
    if path is not None:
        env_file = Path(path)
        if env_file.is_file():
            load_dotenv(env_file)
    else:
        # Find .env in CWD or parent dirs
        env_path = find_dotenv(".env", usecwd=True)
        if env_path:
            load_dotenv(env_path)

    # Collect API keys from environment
    api_keys: dict[str, str] = {}
    for key_name in [
        "BIRDEYE_API_KEY",
        "HELIUS_API_KEY",
        "COINGECKO_API_KEY",
        "OPENAI_API_KEY",
    ]:
        value = os.environ.get(key_name, "")
        if value:
            api_keys[key_name] = value

    demo_mode = not bool(api_keys)

    return KairosConfig(
        api_keys=api_keys,
        demo_mode=demo_mode,
    )


def get_default_config() -> KairosConfig:
    """Return a KairosConfig with factory defaults.

    Returns:
        KairosConfig with all default values.
    """
    return KairosConfig()


def resolve_journal_path(config: KairosConfig) -> Path:
    """Resolve the journal file path.

    Uses ``config.journal_path`` when set, otherwise falls back to
    ``~/.kairos/journal.json``. The parent directory is created if missing.

    Args:
        config: KairosConfig instance.

    Returns:
        Resolved path to the journal file.
    """
    raw = config.journal_path or "~/.kairos/journal.json"
    path = Path(raw).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
