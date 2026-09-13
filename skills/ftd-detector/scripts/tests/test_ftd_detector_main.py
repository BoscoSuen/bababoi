"""End-to-end main() with a mocked market-data client (no network)."""

from __future__ import annotations

import glob
import json
import sys

import ftd_detector
import pytest
from helpers import make_bar


def _history(n=80, start=100.0, step=0.5):
    # Most-recent-first, like PolygonCompatClient.get_historical_prices
    bars = [
        make_bar(start + i * step, date=f"2026-0{1 + i // 28}-{1 + i % 28:02d}") for i in range(n)
    ]
    return list(reversed(bars))


class FakeClient:
    def __init__(self, *a, **k):
        self.calls = []

    def get_historical_prices(self, symbol, days=365):
        self.calls.append(("hist", symbol, days))
        return {"symbol": symbol, "historical": _history()}

    def get_quote(self, symbols):
        self.calls.append(("quote", symbols))
        return [{"symbol": symbols, "price": 123.45}]

    def get_api_stats(self):
        return {
            "cache_entries": 2,
            "api_calls_made": 4,
            "rate_limit_reached": False,
            "provider": "polygon",
            "symbol_proxies": {"^GSPC": "SPY"},
        }

    def get_data_mode(self):
        return "polygon"


def test_main_writes_reports_with_polygon_metadata(tmp_path, monkeypatch):
    monkeypatch.setattr(ftd_detector, "MarketDataClient", FakeClient)
    monkeypatch.setattr(sys, "argv", ["ftd_detector.py", "--output-dir", str(tmp_path)])
    ftd_detector.main()
    files = glob.glob(str(tmp_path / "ftd_detector_*.json"))
    assert len(files) == 1
    data = json.loads(open(files[0]).read())
    assert data["metadata"]["data_source"] == "polygon"
    assert data["metadata"]["symbol_proxies"] == {"^GSPC": "SPY"}
    assert data["metadata"]["index_prices"] == {"sp500": 123.45, "qqq": 123.45}
    assert data["market_state"]["combined_state"]
    assert glob.glob(str(tmp_path / "ftd_detector_*.md"))


def test_main_exits_when_client_cannot_be_built(tmp_path, monkeypatch):
    def boom(*a, **k):
        raise ValueError("Polygon API key required")

    monkeypatch.setattr(ftd_detector, "MarketDataClient", boom)
    monkeypatch.setattr(sys, "argv", ["ftd_detector.py", "--output-dir", str(tmp_path)])
    with pytest.raises(SystemExit) as exc:
        ftd_detector.main()
    assert exc.value.code == 1
