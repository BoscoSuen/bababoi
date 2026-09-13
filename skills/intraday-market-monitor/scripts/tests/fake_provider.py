"""Offline provider for tests: PolygonProvider normalisation over recorded fixtures.

Routes by endpoint name (ignores params) so every ETF/watchlist symbol resolves
to the recorded SPY (or XLK) 5-minute bars.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import _repo_bootstrap

from scripts.market_data.polygon import PolygonProvider

RAW = _repo_bootstrap.REPO_ROOT / "scripts" / "tests" / "fixtures" / "market_data" / "raw"


def load(name: str) -> dict:
    return json.loads((RAW / name).read_text(encoding="utf-8"))


class FakeProvider(PolygonProvider):
    name = "fixture"

    def __init__(self, *, today: date = date(2026, 9, 12), fail_snapshot: bool = False):
        super().__init__(api_key=None, cache=None, offline=False, today=today)
        self.fail_snapshot = fail_snapshot
        self.fetches: list[tuple[str, str]] = []

    def _fetch(self, endpoint, path, params, *, immutable, paged=False, key="results"):
        self.fetches.append((endpoint, path))
        if endpoint == "aggs_5min":
            return load(
                "aggs_5min_XLK_2026-09-11.json"
                if "/XLK/" in path
                else "aggs_5min_SPY_2026-09-11.json"
            )
        if endpoint == "aggs_day":
            return load("aggs_day_AAPL_div.json" if "/AAPL/" in path else "aggs_day_SPY.json")
        if endpoint == "snapshot":
            if self.fail_snapshot and "tickers" not in (params or {}):
                from scripts.market_data.provider import ProviderError

                raise ProviderError("simulated snapshot outage")
            return load("snapshot_tickers_20.json")
        if endpoint == "grouped_daily":
            return load("grouped_daily_2026-09-11_head300.json")
        if endpoint == "dividends":
            return (
                load("dividends_AAPL.json")
                if "AAPL" in json.dumps(params or {})
                else {"results": []}
            )
        if endpoint == "treasury_yields":
            return load("treasury_yields.json")
        if endpoint == "ticker_details":
            return load("ticker_details_BRK.B.json")
        raise AssertionError(f"unexpected endpoint {endpoint}")


def write_fixture_dir(root: Path) -> Path:
    """Materialise a cache-layout directory a FixtureProvider can replay (unused by
    default tests; handy for building replay fixtures)."""
    root.mkdir(parents=True, exist_ok=True)
    return root
