"""Polygon.io REST provider (Stocks Starter plan) with optional disk cache.

Plan facts baked in (verified 2026-09):
- unlimited REST calls, 15-minute delayed, 5 years of history
- aggregates / grouped daily / snapshot / reference / dividends / treasury yields OK
- no indices (``I:VIX`` → NOT_AUTHORIZED) → see ``symbols.YFINANCE_ONLY``
- snapshot rows carry ``day / min / prevDay / todaysChange / todaysChangePerc /
  updated`` but **no** ``lastTrade``
- aggregate ``v`` can be a float (odd-lot / fractional prints) → rounded to int
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from scripts.market_data import timeutil
from scripts.market_data.adjust import apply_dividend_adjustment
from scripts.market_data.cache import DiskCache
from scripts.market_data.http import HttpClient
from scripts.market_data.provider import NotAvailable, ProviderError
from scripts.market_data.symbols import to_polygon

SNAPSHOT_CHUNK = 200
CALENDAR_DAYS_PER_TRADING_DAY = 1.6


class PolygonProvider:
    name = "polygon"

    def __init__(
        self,
        api_key: str | None,
        *,
        session: Any = None,
        cache: DiskCache | None = None,
        offline: bool = False,
        base_url: str | None = None,
        today: date | None = None,
    ) -> None:
        if offline and cache is None:
            raise ValueError("offline provider needs a cache/fixture directory")
        self.cache = cache
        self.offline = offline
        self._today = today  # test seam; None → ET today
        kwargs = {"session": session}
        if base_url:
            kwargs["base_url"] = base_url
        self.http = HttpClient(api_key, **kwargs)
        self._asof: datetime | None = None
        self.symbol_proxies: dict[str, str] = {}
        if offline:
            self.name = "fixture"

    # ------------------------------------------------------------------ core
    def today(self) -> date:
        return self._today or timeutil.now_et().date()

    def _fetch(
        self,
        endpoint: str,
        path: str,
        params: dict | None,
        *,
        immutable: bool,
        paged: bool = False,
        key: str = "results",
    ) -> dict:
        cache_params = {"path": path, **(params or {})}
        if self.cache is not None:
            hit = self.cache.get(endpoint, cache_params)
            if hit is not None:
                return hit
        if self.offline:
            raise NotAvailable(f"fixture miss: {endpoint} {cache_params}")
        payload = (
            self.http.get_paged(path, params, key=key)
            if paged
            else self.http.get_json(path, params)
        )
        payload.pop("request_id", None)
        if self.cache is not None:
            self.cache.put(endpoint, cache_params, payload, immutable=immutable)
        return payload

    def _touch_asof(self, dt: datetime | None) -> None:
        if dt is not None and (self._asof is None or dt > self._asof):
            self._asof = dt

    def _symbol(self, symbol: str) -> str:
        poly, proxied = to_polygon(symbol)
        if proxied:
            self.symbol_proxies[proxied] = poly
        return poly

    # ------------------------------------------------------------ daily bars
    def daily_bars(self, symbol: str, start: date, end: date) -> list[dict]:
        poly = self._symbol(symbol)
        immutable = end < self.today()
        payload = self._fetch(
            "aggs_day",
            f"/v2/aggs/ticker/{poly}/range/1/day/{start.isoformat()}/{end.isoformat()}",
            {"adjusted": "true", "sort": "asc", "limit": 50000},
            immutable=immutable,
            paged=True,
        )
        bars = [self._daily_row(r) for r in payload.get("results") or []]
        bars.sort(key=lambda b: b["date"])
        if bars:
            self._touch_asof(
                datetime.combine(
                    date.fromisoformat(bars[-1]["date"]), timeutil.RTH_CLOSE, tzinfo=timeutil.ET
                )
            )
        try:
            divs = self.dividends(symbol, start=start, end=end + timedelta(days=1))
        except ProviderError:
            divs = []
        return apply_dividend_adjustment(bars, divs)

    def daily_bars_by_count(self, symbol: str, days: int, *, end: date | None = None) -> list[dict]:
        end = end or self.today()
        span = int(days * CALENDAR_DAYS_PER_TRADING_DAY) + 7
        bars = self.daily_bars(symbol, end - timedelta(days=span), end)
        return bars[-days:] if days > 0 else bars

    @staticmethod
    def _daily_row(r: dict) -> dict:
        return {
            "date": timeutil.et_date(int(r["t"])).isoformat(),
            "open": float(r["o"]),
            "high": float(r["h"]),
            "low": float(r["l"]),
            "close": float(r["c"]),
            "adjClose": float(r["c"]),
            "volume": int(round(float(r.get("v") or 0))),
            "vwap": float(r["vw"]) if r.get("vw") is not None else None,
        }

    def grouped_daily(self, session_date: date) -> dict[str, dict]:
        payload = self._fetch(
            "grouped_daily",
            f"/v2/aggs/grouped/locale/us/market/stocks/{session_date.isoformat()}",
            {"adjusted": "true"},
            immutable=session_date < self.today(),
        )
        out: dict[str, dict] = {}
        for r in payload.get("results") or []:
            sym = r.get("T")
            if not sym:
                continue
            row = self._daily_row(r)
            out[sym] = row
        return out

    # ---------------------------------------------------------------- snapshot
    def snapshot(
        self, tickers: list[str] | None = None, *, replay_key: str | None = None
    ) -> list[dict]:
        """All-tickers (or filtered) snapshot. ``replay_key`` (e.g. ``"2026-09-11:1020"``)
        pins the cache entry so a slot can be replayed byte-for-byte."""
        path = "/v2/snapshot/locale/us/markets/stocks/tickers"
        rows: list[dict] = []
        if tickers:
            polys = [self._symbol(t) for t in tickers]
            for i in range(0, len(polys), SNAPSHOT_CHUNK):
                chunk = polys[i : i + SNAPSHOT_CHUNK]
                params: dict = {"tickers": ",".join(chunk)}
                if replay_key:
                    params["replay_key"] = replay_key
                payload = self._fetch("snapshot", path, params, immutable=bool(replay_key))
                rows.extend(payload.get("tickers") or [])
        else:
            params = {"replay_key": replay_key} if replay_key else {}
            payload = self._fetch("snapshot", path, params, immutable=bool(replay_key))
            rows = payload.get("tickers") or []
        out = [self._snapshot_row(r) for r in rows]
        for row in out:
            if row.get("updated_et"):
                self._touch_asof(timeutil.parse_ts_et(row["updated_et"]))
        return out

    @staticmethod
    def _ohlcv(d: dict | None) -> dict | None:
        if not d:
            return None
        try:
            return {
                "o": float(d.get("o", 0) or 0),
                "h": float(d.get("h", 0) or 0),
                "l": float(d.get("l", 0) or 0),
                "c": float(d.get("c", 0) or 0),
                "v": int(round(float(d.get("v", 0) or 0))),
                "vw": float(d["vw"]) if d.get("vw") is not None else None,
            }
        except (TypeError, ValueError):
            return None

    def _snapshot_row(self, r: dict) -> dict:
        updated = r.get("updated")
        updated_et = None
        if updated:
            try:
                updated_et = timeutil.ns_to_et(int(updated)).isoformat()
            except (TypeError, ValueError, OSError):
                updated_et = None
        return {
            "symbol": r.get("ticker"),
            "day": self._ohlcv(r.get("day")),
            "prev_day": self._ohlcv(r.get("prevDay")),
            "minute": self._ohlcv(r.get("min")),
            "change": r.get("todaysChange"),
            "change_pct": r.get("todaysChangePerc"),
            "updated_et": updated_et,
        }

    # ------------------------------------------------------------- intraday
    def bars_5min(self, symbol: str, *, session_date: str, until_et: datetime) -> list[dict]:
        """Confirmed regular-session 5-minute bars (parabolic adapter contract)."""
        if until_et.tzinfo is None:
            raise ValueError("until_et must be timezone-aware")
        until_et = until_et.astimezone(timeutil.ET)
        sdate = date.fromisoformat(session_date)
        bounds = timeutil.session_bounds(sdate)
        if bounds is None:
            return []
        session_open, session_close = bounds
        poly = self._symbol(symbol)
        # Cache key includes the 5-minute floor of until_et so a replayed slot
        # sees the same bars; entries whose session is over are immutable.
        floor = timeutil.floor5(until_et)
        immutable = sdate < self.today() or floor >= session_close
        payload = self._fetch(
            "aggs_5min",
            f"/v2/aggs/ticker/{poly}/range/5/minute/{session_date}/{session_date}",
            {
                "adjusted": "false",
                "sort": "asc",
                "limit": 50000,
                "until_et": floor.isoformat(),
            },
            immutable=immutable,
            paged=True,
        )
        raw = []
        for r in payload.get("results") or []:
            ts = timeutil.ms_to_et(int(r["t"]))
            raw.append(
                {
                    "ts_et": ts.isoformat(),
                    "o": float(r["o"]),
                    "h": float(r["h"]),
                    "l": float(r["l"]),
                    "c": float(r["c"]),
                    "v": int(round(float(r.get("v") or 0))),
                }
            )
        bars = timeutil.rth_filter(
            raw, session_open=session_open, session_close=session_close, until_et=until_et
        )
        if bars:
            self._touch_asof(timeutil.parse_ts_et(bars[-1]["ts_et"]) + timeutil.BAR_5MIN)
        return bars

    # ------------------------------------------------------------ reference
    def treasury_yields(self, *, limit: int = 600) -> list[dict]:
        payload = self._fetch(
            "treasury_yields",
            "/fed/v1/treasury-yields",
            {"limit": min(max(limit, 1), 50000), "sort": "date.desc"},
            immutable=False,
        )
        rows = []
        for r in payload.get("results") or []:
            rows.append(
                {
                    "date": r.get("date"),
                    "month1": r.get("yield_1_month"),
                    "month3": r.get("yield_3_month"),
                    "year1": r.get("yield_1_year"),
                    "year2": r.get("yield_2_year"),
                    "year5": r.get("yield_5_year"),
                    "year10": r.get("yield_10_year"),
                    "year30": r.get("yield_30_year"),
                }
            )
        rows.sort(key=lambda r: r["date"] or "")
        return rows[-limit:]

    def dividends(self, symbol: str, *, start: date, end: date) -> list[dict]:
        poly = self._symbol(symbol)
        payload = self._fetch(
            "dividends",
            "/v3/reference/dividends",
            {
                "ticker": poly,
                "ex_dividend_date.gte": start.isoformat(),
                "ex_dividend_date.lte": end.isoformat(),
                "limit": 1000,
                "sort": "ex_dividend_date",
                "order": "asc",
            },
            immutable=end < self.today(),
            paged=True,
        )
        rows = []
        for r in payload.get("results") or []:
            if not r.get("ex_dividend_date"):
                continue
            rows.append(
                {
                    "ex_date": r["ex_dividend_date"],
                    "cash_amount": float(r.get("cash_amount") or 0),
                    "pay_date": r.get("pay_date"),
                    "frequency": r.get("frequency"),
                    "type": r.get("dividend_type"),
                }
            )
        rows.sort(key=lambda r: r["ex_date"])
        return rows

    def ticker_details(self, symbol: str) -> dict | None:
        poly = self._symbol(symbol)
        try:
            payload = self._fetch(
                "ticker_details", f"/v3/reference/tickers/{poly}", {}, immutable=False
            )
        except NotAvailable:
            return None
        return payload.get("results") or None

    # ---------------------------------------------------------------- meta
    def data_asof(self) -> str | None:
        return self._asof.isoformat() if self._asof else None

    def stats(self) -> dict:
        return {
            "provider": self.name,
            "api_calls_made": self.http.calls_made,
            "cache_hits": self.cache.hits if self.cache else 0,
            "cache_misses": self.cache.misses if self.cache else 0,
            "symbol_proxies": dict(self.symbol_proxies),
        }
