"""Tests for AlpacaBroker."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch

from kairos.brokers.alpaca import AlpacaBroker, AlpacaOrder


class TestAlpacaOrder:
    def test_order_creation(self):
        o = AlpacaOrder(id="123", symbol="AAPL", side="buy", qty=10.0,
                        type="market", status="filled")
        assert o.symbol == "AAPL"
        assert o.side == "buy"


class TestAlpacaBroker:
    def test_not_connected_without_keys(self):
        broker = AlpacaBroker(api_key="", secret_key="")
        assert not broker.is_connected

    def test_connected_with_keys(self):
        broker = AlpacaBroker(api_key="test", secret_key="test")
        assert broker.is_connected

    def test_paper_url_by_default(self):
        broker = AlpacaBroker(api_key="test", secret_key="test")
        assert "paper-api" in broker.base_url

    def test_live_url_when_set(self):
        broker = AlpacaBroker(api_key="test", secret_key="test", live=True)
        assert "api.alpaca.markets" in broker.base_url

    @pytest.mark.asyncio
    async def test_health_check_fails_without_keys(self):
        broker = AlpacaBroker(api_key="", secret_key="")
        result = await broker.health_check()
        assert not result

    @pytest.mark.asyncio
    async def test_place_order_invalid_without_keys(self):
        broker = AlpacaBroker(api_key="", secret_key="")
        with pytest.raises(Exception):
            await broker.place_order("AAPL", "buy", 1.0)
