"""main() data flow with a mocked market-data client (no network).

Covers the provider seam that replaced the vendored FMP client: quotes,
histories, batch fetches, VIX term structure, point-in-time filtering, and
the Polygon metadata (data_source / symbol_proxies) in the report.
"""

from __future__ import annotations

import glob
import json
from datetime import date, timedelta

import market_top_detector as mtd


def _history(n=300, start=400.0, step=0.25, end_date=None):
    end_date = end_date or date.today()
    rows = []
    d = end_date
    for i in range(n):
        while d.weekday() >= 5:
            d -= timedelta(days=1)
        px = start + (n - i) * step
        rows.append(
            {
                "date": d.isoformat(),
                "open": px,
                "high": px * 1.004,
                "low": px * 0.996,
                "close": px,
                "adjClose": px,
                "volume": 1_000_000 + (i % 7) * 10_000,
            }
        )
        d -= timedelta(days=1)
    return rows  # most-recent-first


class FakeClient:
    def __init__(self, *a, **k):
        self.calls = []

    def get_data_mode(self):
        return "polygon"

    def get_quote(self, symbols):
        self.calls.append(("quote", symbols))
        price = 18.0 if symbols == "^VIX" else 475.0
        return [{"symbol": symbols, "price": price, "yearHigh": 500.0, "yearLow": 380.0}]

    def get_historical_prices(self, symbol, days=365):
        self.calls.append(("hist", symbol, days))
        return {"symbol": symbol, "historical": _history(min(days, 300))}

    def get_batch_quotes(self, symbols):
        return {
            s: {"symbol": s, "price": 100.0, "yearHigh": 120.0, "yearLow": 80.0} for s in symbols
        }

    def get_batch_historical(self, symbols, days=50):
        return {s: _history(min(days, 300), start=100.0, step=0.1) for s in symbols}

    def get_vix_term_structure(self):
        return {"vix": 18.0, "vix3m": 20.0, "ratio": 0.9, "classification": "contango"}

    def get_api_stats(self):
        return {
            "cache_entries": 3,
            "api_calls_made": 9,
            "rate_limit_reached": False,
            "provider": "polygon",
            "symbol_proxies": {"^GSPC": "SPY"},
        }


def test_main_runs_end_to_end_with_polygon_client(tmp_path, monkeypatch):
    monkeypatch.setattr(mtd, "MarketDataClient", FakeClient)
    rc = mtd.main(
        [
            "--api-key",
            "x",
            "--output-dir",
            str(tmp_path),
            "--breadth-200dma",
            "62.0",
            "--put-call",
            "0.7",
        ]
    )
    assert rc == 0
    files = glob.glob(str(tmp_path / "market_top_*.json"))
    assert len(files) == 1
    data = json.loads(open(files[0]).read())
    meta = data["metadata"]
    assert meta["data_source"] == "polygon"
    assert meta["data_mode"].startswith("polygon")
    assert meta["symbol_proxies"] == {"^GSPC": "SPY"}
    assert meta["index_data"]["sp500_price"] == 475.0
    assert meta["index_data"]["vix_level"] == 18.0
    assert meta["vix_term_auto"]["classification"] == "contango"
    assert 0 <= data["composite"]["composite_score"] <= 100
    assert set(data["components"]) >= {"distribution_days", "leading_stocks", "index_technical"}


def test_main_exits_1_when_client_unavailable(tmp_path, monkeypatch):
    def boom(*a, **k):
        raise ValueError("Polygon API key required")

    monkeypatch.setattr(mtd, "MarketDataClient", boom)
    import pytest

    with pytest.raises(SystemExit) as exc:
        mtd.main(["--output-dir", str(tmp_path), "--breadth-200dma", "62.0"])
    assert exc.value.code == 1
