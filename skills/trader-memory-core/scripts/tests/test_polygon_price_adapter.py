"""Tests for polygon_price_adapter.py — provider is injected, no network."""

from datetime import date

import polygon_price_adapter
import pytest


class _Provider:
    def __init__(self, bars):
        self.bars = bars
        self.calls = []

    def daily_bars(self, symbol, start, end):
        self.calls.append((symbol, start, end))
        return self.bars


def test_get_daily_closes_prefers_adjclose_and_keeps_order():
    bars = [
        {"date": "2026-03-01", "close": 149.0, "adjClose": 148.5},
        {"date": "2026-03-02", "close": 150.5, "adjClose": 150.0},
        {"date": "2026-03-03", "close": 152.0},
    ]
    provider = _Provider(bars)
    adapter = polygon_price_adapter.PolygonPriceAdapter(provider=provider)
    result = adapter.get_daily_closes("AAPL", "2026-03-01T00:00:00+00:00", "2026-03-03")
    assert result == [
        {"date": "2026-03-01", "close": 148.5},
        {"date": "2026-03-02", "close": 150.0},
        {"date": "2026-03-03", "close": 152.0},
    ]
    assert provider.calls == [("AAPL", date(2026, 3, 1), date(2026, 3, 3))]


def test_empty_history_returns_empty_list():
    adapter = polygon_price_adapter.PolygonPriceAdapter(provider=_Provider([]))
    assert adapter.get_daily_closes("XYZ", "2026-03-01", "2026-03-03") == []


def test_requires_key_without_provider(monkeypatch):
    monkeypatch.delenv("POLYGON_API_KEY", raising=False)
    with pytest.raises(ValueError, match="POLYGON_API_KEY"):
        polygon_price_adapter.PolygonPriceAdapter()


def test_legacy_alias_points_to_polygon_adapter():
    assert polygon_price_adapter.FMPPriceAdapter is polygon_price_adapter.PolygonPriceAdapter
