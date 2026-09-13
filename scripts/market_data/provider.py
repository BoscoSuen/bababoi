"""Provider protocol and error types.

Row shapes (plain dicts, documented here once):

DailyBar (ascending by ``date``)::

    {"date": "YYYY-MM-DD", "open": float, "high": float, "low": float,
     "close": float, "adjClose": float, "volume": int, "vwap": float | None}

IntradayBar (ascending, confirmed bars only; same contract as
``skills/parabolic-short-trade-planner/scripts/adapters/market_data_adapter.py``)::

    {"ts_et": "2026-09-11T09:30:00-04:00", "o": float, "h": float, "l": float,
     "c": float, "v": int}

SnapshotRow::

    {"symbol": str, "day": {"o","h","l","c","v","vw"}, "prev_day": {...},
     "minute": {...} | None, "change": float | None, "change_pct": float | None,
     "updated_et": str | None}

TreasuryRow (ascending by ``date``)::

    {"date": "YYYY-MM-DD", "month1", "month3", "year1", "year2", "year5",
     "year10", "year30": float | None}

Dividend (ascending by ``ex_date``)::

    {"ex_date": "YYYY-MM-DD", "cash_amount": float, "pay_date": str | None,
     "frequency": int | None, "type": str | None}
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Protocol


class ProviderError(RuntimeError):
    """Transport or payload failure after retries."""


class NotAvailable(ProviderError):
    """The provider (or plan tier) cannot serve this symbol/endpoint."""


class MarketDataProvider(Protocol):
    name: str

    def daily_bars(self, symbol: str, start: date, end: date) -> list[dict]: ...

    def daily_bars_by_count(
        self, symbol: str, days: int, *, end: date | None = None
    ) -> list[dict]: ...

    def grouped_daily(self, session_date: date) -> dict[str, dict]: ...

    def snapshot(self, tickers: list[str] | None = None) -> list[dict]: ...

    def bars_5min(self, symbol: str, *, session_date: str, until_et: datetime) -> list[dict]: ...

    def treasury_yields(self, *, limit: int = 600) -> list[dict]: ...

    def dividends(self, symbol: str, *, start: date, end: date) -> list[dict]: ...

    def ticker_details(self, symbol: str) -> dict | None: ...

    def data_asof(self) -> str | None: ...

    def stats(self) -> dict: ...
