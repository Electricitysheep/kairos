"""Alpaca Broker — paper and live trading via REST API.

Requires: ALPACA_API_KEY_ID and ALPACA_SECRET_KEY environment variables.
Paper trading: uses alpaca.markets (default)
Live trading: uses api.alpaca.markets (set ALPACA_LIVE=true)
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class AlpacaOrder:
    """Represents a trade order placed via Alpaca."""

    id: str
    symbol: str
    side: str  # "buy" or "sell"
    qty: float
    type: str  # "market" or "limit"
    status: str  # "filled", "pending", "rejected"
    filled_qty: float = 0.0
    filled_avg_price: float = 0.0
    created_at: str = ""


class AlpacaBroker:
    """Lightweight Alpaca Trading API client.

    Uses httpx (no alpaca-py dependency needed).
    Supports paper trading by default; set ALPACA_LIVE=true for real money.
    """

    PAPER_URL = "https://paper-api.alpaca.markets"
    LIVE_URL = "https://api.alpaca.markets"

    def __init__(self, api_key: str = "", secret_key: str = "", live: bool = False):
        self.api_key = api_key or os.environ.get("ALPACA_API_KEY_ID", "")
        self.secret_key = secret_key or os.environ.get("ALPACA_SECRET_KEY", "")
        self.live = live or os.environ.get("ALPACA_LIVE", "").lower() in ("true", "1")
        self.base_url = self.LIVE_URL if self.live else self.PAPER_URL
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "APCA-API-KEY-ID": self.api_key,
                "APCA-SECRET-KEY": self.secret_key,
            },
            timeout=15,
        )

    @property
    def is_connected(self) -> bool:
        return bool(self.api_key and self.secret_key)

    async def get_account(self) -> dict:
        """Get account info: equity, cash, buying power."""
        r = await self._client.get("/v2/account")
        r.raise_for_status()
        data = r.json()
        return {
            "equity": float(data.get("equity", 0)),
            "cash": float(data.get("cash", 0)),
            "buying_power": float(data.get("buying_power", 0)),
            "status": data.get("status", ""),
            "daytrade_count": data.get("daytrade_count", 0),
        }

    async def get_positions(self) -> list[dict]:
        """Get current open positions."""
        r = await self._client.get("/v2/positions")
        r.raise_for_status()
        positions = []
        for p in r.json():
            positions.append(
                {
                    "symbol": p.get("symbol", ""),
                    "qty": float(p.get("qty", 0)),
                    "market_value": float(p.get("market_value", 0)),
                    "cost_basis": float(p.get("cost_basis", 0)),
                    "unrealized_pl": float(p.get("unrealized_pl", 0)),
                    "current_price": float(p.get("current_price", 0)),
                }
            )
        return positions

    async def place_order(self, symbol: str, side: str, qty: float, order_type: str = "market") -> AlpacaOrder:
        """Place a market or limit order."""
        data: dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "qty": str(qty),
            "time_in_force": "day",
        }
        r = await self._client.post("/v2/orders", json=data)
        r.raise_for_status()
        o = r.json()
        return AlpacaOrder(
            id=o.get("id", ""),
            symbol=o.get("symbol", ""),
            side=o.get("side", ""),
            qty=float(o.get("qty", 0)),
            type=o.get("type", ""),
            status=o.get("status", ""),
            filled_qty=float(o.get("filled_qty", 0)),
            filled_avg_price=float(o.get("filled_avg_price", 0)),
            created_at=o.get("created_at", ""),
        )

    async def close_position(self, symbol: str) -> bool:
        """Close an open position."""
        r = await self._client.delete(f"/v2/positions/{symbol}")
        return r.status_code == 200

    async def close_all_positions(self) -> list[dict]:
        """Close all open positions."""
        r = await self._client.delete("/v2/positions")
        if r.status_code == 200:
            return r.json()
        return []

    async def get_orders(self, status: str = "closed", limit: int = 25) -> list[AlpacaOrder]:
        """Get recent orders."""
        r = await self._client.get("/v2/orders", params={"status": status, "limit": limit})
        r.raise_for_status()
        return [
            AlpacaOrder(
                id=o.get("id", ""),
                symbol=o.get("symbol", ""),
                side=o.get("side", ""),
                qty=float(o.get("qty", 0)),
                type=o.get("type", ""),
                status=o.get("status", ""),
                filled_qty=float(o.get("filled_qty", 0)),
                filled_avg_price=float(o.get("filled_avg_price", 0)),
                created_at=o.get("created_at", ""),
            )
            for o in r.json()
        ]

    async def health_check(self) -> bool:
        """Check if API is accessible."""
        if not self.is_connected:
            return False
        try:
            await self.get_account()
            return True
        except Exception:
            return False

    async def close(self):
        await self._client.aclose()
