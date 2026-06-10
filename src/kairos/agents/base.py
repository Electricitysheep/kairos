"""Base classes for Kairos agents."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field


class AgentContext(BaseModel):
    """Context passed to an agent during processing."""

    input_data: dict = Field(default_factory=dict)
    config: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)


def _utc_timestamp() -> str:
    """Generate a UTC ISO format timestamp."""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


class AgentResult(BaseModel):
    """Result returned by an agent after processing."""

    agent_name: str
    output: dict = Field(default_factory=dict)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reasoning: str = ""
    metadata: dict = Field(default_factory=dict)
    timestamp: str = Field(default_factory=_utc_timestamp)


class AgentBase(ABC):
    """Abstract base class for all Kairos agents."""

    def __init__(self, config: dict | None = None) -> None:
        """Initialize the agent with optional configuration."""
        self._config = config or {}

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    async def process(self, context: AgentContext) -> AgentResult: ...