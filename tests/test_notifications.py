"""Tests for the notifications module."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

from kairos.notifications import (
    ConsoleNotifier,
    MultiNotifier,
    Notifier,
    TradeAlert,
    WebhookNotifier,
)


class _FakeResponse:
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code


class _RecordingClient:
    def __init__(self, status_code: int = 200) -> None:
        self.status_code = status_code
        self.calls: list[dict] = []

    async def post(self, url, json=None, timeout=None):
        self.calls.append({"url": url, "json": json, "timeout": timeout})
        return _FakeResponse(self.status_code)


class _CountingNotifier(Notifier):
    def __init__(self, result: bool = True) -> None:
        self.result = result
        self.count = 0

    async def send(self, alert: TradeAlert) -> bool:
        self.count += 1
        return self.result


class TestTradeAlert:
    def test_format_buy_with_reason(self):
        alert = TradeAlert("AAPL", "buy", 0.75, "RSI oversold")
        out = alert.format()
        assert "BUY AAPL" in out
        assert "75%" in out
        assert "RSI oversold" in out

    def test_format_without_reason_is_single_line(self):
        alert = TradeAlert("SOL", "HOLD", 0.5)
        assert "\n" not in alert.format()

    def test_unknown_decision_uses_bullet(self):
        assert "•" in TradeAlert("X", "wat", 0.1).format()


class TestConsoleNotifier:
    def test_prints_formatted_alert(self):
        captured: list[str] = []
        notifier = ConsoleNotifier(printer=captured.append)
        ok = asyncio.run(notifier.send(TradeAlert("AAPL", "BUY", 0.6)))
        assert ok is True
        assert len(captured) == 1
        assert "BUY AAPL" in captured[0]


class TestMultiNotifier:
    def test_fans_out_to_all(self):
        a, b = _CountingNotifier(), _CountingNotifier()
        ok = asyncio.run(MultiNotifier([a, b]).send(TradeAlert("SOL", "SELL", 0.9)))
        assert ok is True
        assert a.count == 1 and b.count == 1

    def test_fails_if_any_fails(self):
        a, b = _CountingNotifier(True), _CountingNotifier(False)
        ok = asyncio.run(MultiNotifier([a, b]).send(TradeAlert("SOL", "SELL", 0.9)))
        assert ok is False


class TestWebhookNotifier:
    def test_posts_payload_and_returns_true_on_2xx(self):
        client = _RecordingClient(status_code=200)
        notifier = WebhookNotifier("https://hook.test/x", client=client)
        ok = asyncio.run(notifier.send(TradeAlert("AAPL", "BUY", 0.6)))
        assert ok is True
        assert client.calls[0]["url"] == "https://hook.test/x"
        assert "BUY AAPL" in client.calls[0]["json"]["text"]

    def test_returns_false_on_error_status(self):
        client = _RecordingClient(status_code=500)
        notifier = WebhookNotifier("https://hook.test/x", client=client)
        assert asyncio.run(notifier.send(TradeAlert("AAPL", "BUY", 0.6))) is False

    def test_extra_payload_is_merged(self):
        client = _RecordingClient()
        notifier = WebhookNotifier(
            "https://api.telegram.org/botX/sendMessage",
            extra_payload={"chat_id": "123"},
            client=client,
        )
        asyncio.run(notifier.send(TradeAlert("SOL", "HOLD", 0.5)))
        assert client.calls[0]["json"]["chat_id"] == "123"

    def test_default_path_creates_httpx_client(self):
        with patch("kairos.notifications.webhook.httpx.AsyncClient") as mock_cls:
            client = mock_cls.return_value
            client.__aenter__ = AsyncMock(return_value=client)
            client.__aexit__ = AsyncMock(return_value=None)
            client.post = AsyncMock(return_value=_FakeResponse(204))
            notifier = WebhookNotifier("https://hook.test/x")
            ok = asyncio.run(notifier.send(TradeAlert("AAPL", "BUY", 0.6)))
            assert ok is True
            client.post.assert_awaited_once()
