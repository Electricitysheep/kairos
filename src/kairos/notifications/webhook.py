"""Webhook notifier — POSTs alerts to Slack, Discord, Telegram, or a custom URL."""

from __future__ import annotations

from typing import Any

import httpx

from kairos.notifications.base import Notifier, TradeAlert


class WebhookNotifier(Notifier):
    """POST alerts to a generic JSON webhook.

    The request body is ``{payload_key: <formatted alert>}`` merged with
    ``extra_payload``. Examples:

    - Slack / Discord: ``WebhookNotifier(url)`` (default ``payload_key="text"``)
    - Telegram: ``WebhookNotifier("https://api.telegram.org/bot<token>/sendMessage",
      extra_payload={"chat_id": "<id>"})``
    """

    def __init__(
        self,
        url: str,
        *,
        payload_key: str = "text",
        extra_payload: dict[str, Any] | None = None,
        timeout: float = 10.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._url = url
        self._payload_key = payload_key
        self._extra = dict(extra_payload or {})
        self._timeout = timeout
        self._client = client

    async def send(self, alert: TradeAlert) -> bool:
        payload: dict[str, Any] = {self._payload_key: alert.format(), **self._extra}
        if self._client is not None:
            response = await self._client.post(self._url, json=payload, timeout=self._timeout)
        else:
            async with httpx.AsyncClient() as client:
                response = await client.post(self._url, json=payload, timeout=self._timeout)
        return 200 <= response.status_code < 300
