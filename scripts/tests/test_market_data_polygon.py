"""PolygonProvider against recorded fixtures via a fake session (no network)."""

from __future__ import annotations

import sys
from datetime import date, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pytest  # noqa: E402

from scripts.market_data import get_provider
from scripts.market_data.cache import DiskCache
from scripts.market_data.http import HttpClient, redact
from scripts.market_data.polygon import PolygonProvider
from scripts.market_data.provider import NotAvailable, ProviderError
from scripts.market_data.timeutil import ET
from scripts.tests import market_data_helpers as helpers  # noqa: E402

TODAY = date(2026, 9, 12)


@pytest.fixture
def provider(tmp_path):
    session = helpers.FakeSession(helpers.polygon_routes())
    p = PolygonProvider(
        "FAKEKEY", session=session, cache=DiskCache(tmp_path), today=TODAY
    )  # pragma: allowlist secret
    p.http.min_interval = 0
    return p


def test_daily_bars_ascending_with_adjclose_and_int_volume(provider):
    bars = provider.daily_bars("SPY", date(2026, 7, 1), date(2026, 9, 11))
    assert bars and bars[0]["date"] < bars[-1]["date"]
    row = bars[-1]
    assert set(row) == {"date", "open", "high", "low", "close", "adjClose", "volume", "vwap"}
    assert isinstance(row["volume"], int)
    assert row["date"] == "2026-09-11"


def test_aapl_adjclose_reflects_august_dividend(provider):
    bars = provider.daily_bars("AAPL", date(2026, 7, 20), date(2026, 8, 31))
    before = [b for b in bars if b["date"] < "2026-08-10"]
    after = [b for b in bars if b["date"] >= "2026-08-10"]
    assert all(b["adjClose"] < b["close"] for b in before)
    assert all(b["adjClose"] == b["close"] for b in after)
    ratios = {round(b["adjClose"] / b["close"], 6) for b in before}
    assert len(ratios) == 1  # constant factor before the ex-date


def test_daily_bars_by_count_trims_to_requested_length(provider):
    bars = provider.daily_bars_by_count("SPY", 5, end=date(2026, 9, 11))
    assert len(bars) == 5 and bars[-1]["date"] == "2026-09-11"


def test_index_symbols_are_proxied_and_recorded(provider):
    bars = provider.daily_bars_by_count("^GSPC", 3, end=date(2026, 9, 11))
    assert bars
    assert provider.symbol_proxies == {"^GSPC": "SPY"}
    assert provider.stats()["symbol_proxies"] == {"^GSPC": "SPY"}


def test_vix_is_not_available(provider):
    with pytest.raises(NotAvailable):
        provider.daily_bars_by_count("^VIX", 5)


def test_snapshot_normalises_rows_without_lasttrade(provider):
    rows = provider.snapshot(["SPY", "BRK-B", "AAPL"])
    by = {r["symbol"]: r for r in rows}
    assert "BRK.B" in by  # dash → dot mapping travelled through
    spy = by["SPY"]
    assert spy["day"]["c"] > 0 and spy["prev_day"]["c"] > 0 and spy["day"]["vw"] is not None
    assert spy["updated_et"].startswith("2026-09-11T")
    assert provider.data_asof() is not None


def test_bars_5min_filters_to_confirmed_rth_bars(provider):
    until = datetime(2026, 9, 11, 10, 20, tzinfo=ET)  # slot 10:20 → data through 10:05
    bars = provider.bars_5min("SPY", session_date="2026-09-11", until_et=until)
    assert bars[0]["ts_et"] == "2026-09-11T09:30:00-04:00"
    assert bars[-1]["ts_et"] == "2026-09-11T10:15:00-04:00"  # closes 10:20 <= until
    assert all(isinstance(b["v"], int) for b in bars)
    assert provider.data_asof() == "2026-09-11T10:20:00-04:00"


def test_bars_5min_weekend_returns_empty(provider):
    until = datetime(2026, 9, 12, 12, 0, tzinfo=ET)
    assert provider.bars_5min("SPY", session_date="2026-09-12", until_et=until) == []


def test_bars_5min_requires_aware_until(provider):
    with pytest.raises(ValueError):
        provider.bars_5min("SPY", session_date="2026-09-11", until_et=datetime(2026, 9, 11, 10))


def test_treasury_yields_ascending_mapped_fields(provider):
    rows = provider.treasury_yields(limit=10)
    assert rows[0]["date"] <= rows[-1]["date"]
    assert rows[-1]["year10"] == 4.83 and rows[-1]["year2"] == 4.43


def test_dividends_and_ticker_details(provider):
    # The fake session ignores the ex_dividend_date filter, so assert on shape,
    # ordering, and the presence of the August 2026 row rather than exact equality.
    divs = provider.dividends("AAPL", start=date(2026, 7, 1), end=date(2026, 9, 1))
    assert divs == sorted(divs, key=lambda d: d["ex_date"])
    assert {
        "ex_date": "2026-08-10",
        "cash_amount": 0.27,
        "pay_date": "2026-08-13",
        "frequency": 4,
        "type": "CD",
    } in divs
    details = provider.ticker_details("BRK-B")
    assert details["ticker"] == "BRK.B" and details["market_cap"] > 0
    assert provider.ticker_details("ZZZZ") is None


def test_grouped_daily_keys_by_symbol(provider):
    rows = provider.grouped_daily(date(2026, 9, 11))
    assert len(rows) == 300
    sym, row = next(iter(rows.items()))
    assert row["date"] == "2026-09-11" and isinstance(row["volume"], int)


def test_cache_makes_second_call_free_and_fixture_provider_replays(provider, tmp_path):
    provider.daily_bars("SPY", date(2026, 7, 1), date(2026, 9, 11))
    calls = provider.http.calls_made
    provider.daily_bars("SPY", date(2026, 7, 1), date(2026, 9, 11))
    assert provider.http.calls_made == calls  # served from cache
    replay = get_provider("fixture", fixture_dir=tmp_path)
    assert replay.name == "fixture"
    bars = replay.daily_bars("SPY", date(2026, 7, 1), date(2026, 9, 11))
    assert bars[-1]["date"] == "2026-09-11"
    with pytest.raises(NotAvailable):
        replay.daily_bars("MSFT", date(2026, 7, 1), date(2026, 9, 11))


def test_http_retries_then_raises_and_redacts_key():
    slept = []
    boom = helpers.FakeResponse(
        {"message": "rate limited apiKey=SECRET1"}, 429, {"Retry-After": "2"}
    )
    session = helpers.FakeSession({"/x": [boom, boom, boom, boom]})
    client = HttpClient(
        "SECRET1", session=session, max_retries=2, min_interval=0, sleep=slept.append
    )  # pragma: allowlist secret
    with pytest.raises(ProviderError) as exc:
        client.get_json("/x")
    assert slept == [2.0, 2.0]
    assert "SECRET1" not in str(exc.value)


def test_http_403_is_not_available_and_paging_follows_next_url():
    session = helpers.FakeSession(
        {
            "/forbidden": helpers.FakeResponse(
                {"status": "NOT_AUTHORIZED", "message": "upgrade"}, 403
            ),
            "/paged?cursor=2": {"results": [3], "status": "OK"},
            "/paged": {"results": [1, 2], "next_url": "https://api.polygon.io/paged?cursor=2"},
        }
    )
    client = HttpClient("K", session=session, min_interval=0)  # pragma: allowlist secret
    with pytest.raises(NotAvailable):
        client.get_json("/forbidden")
    out = client.get_paged("/paged")
    assert out["results"] == [1, 2, 3] and "next_url" not in out
    assert session.calls[-1][0].endswith("cursor=2")


def test_redact_helper():
    assert (
        redact("https://x/y?apiKey=abc123&x=1", "abc123") == "https://x/y?apiKey=***REDACTED***&x=1"
    )
    assert redact(None) is None


def test_get_provider_requires_key(monkeypatch):
    monkeypatch.delenv("POLYGON_API_KEY", raising=False)
    with pytest.raises(ValueError):
        get_provider("polygon")
    with pytest.raises(ValueError):
        get_provider("nope")
