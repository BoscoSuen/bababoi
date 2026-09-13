"""Shared helpers for scripts/tests/test_market_data_*.py (not a test module)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

FIXTURES = REPO_ROOT / "scripts" / "tests" / "fixtures" / "market_data" / "raw"


def load_fixture(name: str) -> dict:
    with (FIXTURES / name).open("r", encoding="utf-8") as fh:
        return json.load(fh)


class FakeResponse:
    def __init__(self, payload: Any, status: int = 200, headers: dict | None = None):
        self._payload = payload
        self.status_code = status
        self.headers = headers or {}
        self.text = json.dumps(payload) if not isinstance(payload, str) else payload

    def json(self):
        if isinstance(self._payload, str):
            raise ValueError("not json")
        return json.loads(json.dumps(self._payload))  # deep copy


class FakeSession:
    """Routes GETs by URL substring → payload (or a list of responses in order)."""

    def __init__(self, routes: dict[str, Any]):
        self.routes = routes
        self.calls: list[tuple[str, dict]] = []

    def get(self, url, params=None, headers=None, timeout=None):
        self.calls.append((url, dict(params or {})))
        assert "apiKey" not in (params or {}), "key must travel in the header only"
        for needle, payload in self.routes.items():
            if needle in url:
                if isinstance(payload, list):
                    nxt = payload.pop(0) if len(payload) > 1 else payload[0]
                    return nxt if isinstance(nxt, FakeResponse) else FakeResponse(nxt)
                return payload if isinstance(payload, FakeResponse) else FakeResponse(payload)
        return FakeResponse({"status": "NOT_FOUND", "message": f"no route for {url}"}, 404)


def polygon_routes() -> dict[str, Any]:
    """Routes wired to the recorded fixtures."""
    return {
        "/v2/aggs/ticker/SPY/range/1/day/": load_fixture("aggs_day_SPY.json"),
        "/v2/aggs/ticker/AAPL/range/1/day/": load_fixture("aggs_day_AAPL_div.json"),
        "/v2/aggs/ticker/SPY/range/5/minute/": load_fixture("aggs_5min_SPY_2026-09-11.json"),
        "/v2/aggs/ticker/XLK/range/5/minute/": load_fixture("aggs_5min_XLK_2026-09-11.json"),
        "/v2/snapshot/locale/us/markets/stocks/tickers": load_fixture("snapshot_tickers_20.json"),
        "/v3/reference/dividends": load_fixture("dividends_AAPL.json"),
        "/fed/v1/treasury-yields": load_fixture("treasury_yields.json"),
        "/v3/reference/tickers/BRK.B": load_fixture("ticker_details_BRK.B.json"),
        "/v2/aggs/grouped/locale/us/market/stocks/": load_fixture(
            "grouped_daily_2026-09-11_head300.json"
        ),
    }
