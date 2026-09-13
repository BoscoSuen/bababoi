"""PolygonCompatClient reproduces the FMP shapes migrated skills expect."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pytest  # noqa: E402

from scripts.market_data import legacy
from scripts.market_data.cache import DiskCache
from scripts.market_data.legacy import PolygonCompatClient
from scripts.market_data.polygon import PolygonProvider
from scripts.tests import market_data_helpers as helpers  # noqa: E402


@pytest.fixture
def client(tmp_path):
    session = helpers.FakeSession(helpers.polygon_routes())
    provider = PolygonProvider(
        "FAKEKEY",
        session=session,
        cache=DiskCache(tmp_path),
        today=date(2026, 9, 12),  # pragma: allowlist secret
    )
    provider.http.min_interval = 0
    return PolygonCompatClient(provider=provider)


def test_requires_key_without_provider(monkeypatch):
    monkeypatch.delenv("POLYGON_API_KEY", raising=False)
    with pytest.raises(ValueError, match="POLYGON_API_KEY"):
        PolygonCompatClient()


def test_historical_prices_fmp_shape_descending(client):
    data = client.get_historical_prices("SPY", days=10)
    assert data["symbol"] == "SPY"
    hist = data["historical"]
    assert len(hist) == 10
    assert hist[0]["date"] > hist[-1]["date"]  # newest first
    assert set(hist[0]) == {"date", "open", "high", "low", "close", "adjClose", "volume"}
    # second call served from the compat cache
    assert client.get_historical_prices("SPY", days=10) is data


def test_batch_historical_returns_inner_lists(client):
    out = client.get_batch_historical(["SPY", "^GSPC"], days=5)
    assert set(out) == {"SPY", "^GSPC"} and len(out["^GSPC"]) == 5


def test_quote_fields_from_snapshot_and_history(client):
    quotes = client.get_quote("SPY,AAPL")
    assert [q["symbol"] for q in quotes] == ["SPY", "AAPL"]
    q = quotes[0]
    for field in (
        "price",
        "previousClose",
        "change",
        "changesPercentage",
        "open",
        "dayHigh",
        "dayLow",
        "volume",
        "avgVolume",
        "yearHigh",
        "yearLow",
        "marketCap",
    ):
        assert field in q, field
    assert q["price"] == 764.29  # snapshot day close for SPY
    assert q["yearHigh"] >= q["price"] >= q["yearLow"]


def test_batch_quotes_with_market_cap(client):
    client.include_market_cap = True
    quotes = client.get_batch_quotes(["BRK-B"])
    assert quotes["BRK-B"]["marketCap"] > 1e11


def test_treasury_rates_newest_first(client):
    rows = client.get_treasury_rates(days=10)
    assert rows[0]["date"] >= rows[-1]["date"]
    assert rows[0]["year10"] == 4.83


def test_vix_term_structure_uses_yfinance_fallback(client, monkeypatch):
    def fake_quote(symbol):
        return {"^VIX": {"price": 18.0}, "^VIX3M": {"price": 20.0}}[symbol]

    monkeypatch.setattr(legacy.PolygonCompatClient, "_yf_quote", staticmethod(fake_quote))
    ts = client.get_vix_term_structure()
    assert ts["ratio"] == 0.9 and ts["classification"] == "contango"


def test_vix_quote_routes_to_yfinance_not_polygon(client, monkeypatch):
    monkeypatch.setattr(
        legacy.PolygonCompatClient,
        "_yf_quote",
        staticmethod(lambda s: {"symbol": s, "price": 15.5}),
    )
    quotes = client.get_quote("^VIX")
    assert quotes[0]["price"] == 15.5


def test_sp500_constituents_uses_public_csv(client, monkeypatch):
    csv_text = "Symbol,Security,GICS Sector,GICS Sub-Industry\nAAPL,Apple,IT,Tech Hardware\nBRK.B,Berkshire,Financials,Multi\n"

    class R:
        status_code = 200
        text = csv_text

    class S:
        def get(self, url, timeout=30):
            return R()

    from scripts.market_data import universe

    monkeypatch.setattr(legacy, "sp500_constituents", lambda: universe.sp500_constituents(S()))
    rows = client.get_sp500_constituents()
    assert rows[1] == {
        "symbol": "BRK.B",
        "name": "Berkshire",
        "sector": "Financials",
        "subSector": "Multi",
    }


def test_api_stats_shape(client):
    client.get_historical_prices("SPY", days=3)
    stats = client.get_api_stats()
    assert {"cache_entries", "api_calls_made", "rate_limit_reached", "provider"} <= set(stats)
    assert stats["provider"] == "polygon" and client.get_data_mode() == "polygon"
