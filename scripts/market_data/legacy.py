"""FMP-shaped compatibility client on top of a :class:`MarketDataProvider`.

Migrated skills used to construct ``fmp_client.FMPClient(api_key)`` and read:

- ``get_historical_prices(symbol, days)`` → ``{"symbol", "historical": [...]}``
  with rows **descending** (newest first) ``date/open/high/low/close/adjClose/volume``
- ``get_quote(symbols)`` → ``[{"symbol", "price", "previousClose", ...}]``
- ``get_batch_quotes`` / ``get_batch_historical`` / ``get_treasury_rates`` /
  ``get_sp500_constituents`` / ``get_vix_term_structure`` / ``get_api_stats``

This class keeps those signatures and shapes so the skill bodies stay intact.
"""

from __future__ import annotations

import sys
from datetime import date
from typing import Any

from scripts.market_data import get_provider, resolve_api_key
from scripts.market_data.provider import MarketDataProvider, NotAvailable, ProviderError
from scripts.market_data.symbols import YFINANCE_ONLY
from scripts.market_data.universe import sp500_constituents


class ApiCallBudgetExceeded(RuntimeError):
    """Kept for callers that still catch the FMP-era budget error."""


class PolygonCompatClient:
    """Drop-in replacement for the vendored ``FMPClient`` classes."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        provider: MarketDataProvider | None = None,
        max_api_calls: int | None = None,
        include_market_cap: bool = False,
        fixture_dir: str | None = None,
    ) -> None:
        if provider is None:
            if fixture_dir:
                provider = get_provider("fixture", fixture_dir=fixture_dir)
            else:
                key = resolve_api_key(api_key)
                if not key:
                    raise ValueError(
                        "Polygon API key required. Set POLYGON_API_KEY env var or pass --api-key."
                    )
                provider = get_provider("polygon", api_key=key)
        self.provider = provider
        self.api_key = api_key
        self.max_api_calls = max_api_calls  # informational only; Starter is unlimited
        self.include_market_cap = include_market_cap
        self.cache: dict[str, Any] = {}
        self._quote_history_days = 260
        self.rate_limit_reached = False

    # ----------------------------------------------------------- history
    def get_historical_prices(self, symbol: str, days: int = 365) -> dict | None:
        """FMP v3 shape: ``{"symbol": ..., "historical": [newest first]}`` or ``None``."""
        key = f"hist_{symbol}_{days}"
        if key in self.cache:
            return self.cache[key]
        try:
            bars = self.provider.daily_bars_by_count(symbol, days)
        except NotAvailable:
            rows = self._yf_history(symbol, days)
            if rows is None:
                return None
            bars = rows
        except ProviderError as exc:
            print(f"WARN: historical fetch failed for {symbol}: {exc}", file=sys.stderr)
            return None
        if not bars:
            return None
        historical = [
            {
                "date": b["date"],
                "open": b["open"],
                "high": b["high"],
                "low": b["low"],
                "close": b["close"],
                "adjClose": b.get("adjClose", b["close"]),
                "volume": b["volume"],
            }
            for b in reversed(bars)
        ]
        data = {"symbol": symbol, "historical": historical}
        self.cache[key] = data
        return data

    def get_batch_historical(self, symbols: list[str], days: int = 260) -> dict[str, list[dict]]:
        out: dict[str, list[dict]] = {}
        for sym in symbols:
            data = self.get_historical_prices(sym, days)
            if data and data.get("historical"):
                out[sym] = data["historical"]
        return out

    # ------------------------------------------------------------ quotes
    def get_quote(self, symbols: str) -> list[dict] | None:
        """FMP ``/quote`` shape for one or more comma-separated symbols."""
        syms = [s.strip() for s in symbols.split(",") if s.strip()]
        quotes = self.get_batch_quotes(syms)
        rows = [quotes[s] for s in syms if s in quotes]
        return rows or None

    def get_batch_quotes(self, symbols: list[str]) -> dict[str, dict]:
        out: dict[str, dict] = {}
        pending = []
        for sym in symbols:
            key = f"quote_{sym}"
            if key in self.cache:
                out[sym] = self.cache[key]
            elif sym.upper() in YFINANCE_ONLY:
                q = self._yf_quote(sym)
                if q:
                    out[sym] = q
                    self.cache[key] = q
            else:
                pending.append(sym)
        if not pending:
            return out
        snap: dict[str, dict] = {}
        try:
            for row in self.provider.snapshot(pending):
                if row.get("symbol"):
                    snap[row["symbol"]] = row
        except ProviderError as exc:
            print(f"WARN: snapshot failed: {exc}", file=sys.stderr)
        for sym in pending:
            poly = _polygon_key(sym)
            q = self._build_quote(sym, snap.get(poly))
            if q:
                out[sym] = q
                self.cache[f"quote_{sym}"] = q
        return out

    def _build_quote(self, symbol: str, snap: dict | None) -> dict | None:
        try:
            bars = self.provider.daily_bars_by_count(symbol, self._quote_history_days)
        except ProviderError:
            bars = []
        day = (snap or {}).get("day") or {}
        prev = (snap or {}).get("prev_day") or {}
        if not bars and not day.get("c"):
            return None
        last_bar = bars[-1] if bars else None
        price = day.get("c") or (last_bar["close"] if last_bar else 0.0)
        prev_close = prev.get("c") or (
            bars[-2]["close"] if len(bars) > 1 else (last_bar["close"] if last_bar else price)
        )
        change = price - prev_close if prev_close else 0.0
        highs = [b["high"] for b in bars] + ([day["h"]] if day.get("h") else [])
        lows = [b["low"] for b in bars] + ([day["l"]] if day.get("l") else [])
        vols = [b["volume"] for b in bars]
        quote = {
            "symbol": symbol,
            "name": symbol,
            "price": price,
            "previousClose": prev_close,
            "change": round(change, 4),
            "changesPercentage": round(change / prev_close * 100, 4) if prev_close else 0.0,
            "changePercentage": round(change / prev_close * 100, 4) if prev_close else 0.0,
            "open": day.get("o") or (last_bar["open"] if last_bar else price),
            "dayHigh": day.get("h") or (last_bar["high"] if last_bar else price),
            "dayLow": day.get("l") or (last_bar["low"] if last_bar else price),
            "volume": day.get("v") or (last_bar["volume"] if last_bar else 0),
            "avgVolume": int(sum(vols) / len(vols)) if vols else 0,
            "yearHigh": max(highs) if highs else price,
            "yearLow": min(lows) if lows else price,
            "priceAvg50": _sma(bars, 50),
            "priceAvg200": _sma(bars, 200),
            "marketCap": 0,
            "exchange": None,
            "timestamp": (snap or {}).get("updated_et"),
        }
        if self.include_market_cap:
            details = self.provider.ticker_details(symbol) or {}
            quote["marketCap"] = float(details.get("market_cap") or 0)
            quote["name"] = details.get("name") or symbol
            quote["exchange"] = details.get("primary_exchange")
        return quote

    # ------------------------------------------------------------- macro
    def get_treasury_rates(self, days: int = 600) -> list[dict] | None:
        """FMP ``/treasury-rates`` shape (newest first): ``date, month1, month3, year1,
        year2, year5, year10, year30``."""
        try:
            rows = self.provider.treasury_yields(limit=days)
        except ProviderError as exc:
            print(f"WARN: treasury yields failed: {exc}", file=sys.stderr)
            return None
        return list(reversed(rows)) or None

    def get_vix_term_structure(self) -> dict | None:
        vix = self._yf_quote("^VIX")
        vix3m = self._yf_quote("^VIX3M")
        if not vix or not vix3m or not vix3m.get("price"):
            return None
        ratio = vix["price"] / vix3m["price"]
        if ratio < 0.85:
            classification = "steep_contango"
        elif ratio < 0.95:
            classification = "contango"
        elif ratio <= 1.05:
            classification = "flat"
        else:
            classification = "backwardation"
        return {
            "vix": round(vix["price"], 2),
            "vix3m": round(vix3m["price"], 2),
            "ratio": round(ratio, 3),
            "classification": classification,
        }

    # ---------------------------------------------------------- universe
    def get_sp500_constituents(self) -> list[dict] | None:
        key = "sp500_constituents"
        if key not in self.cache:
            data = sp500_constituents()
            if data:
                self.cache[key] = data
        return self.cache.get(key)

    # --------------------------------------------------------------- meta
    def get_data_mode(self) -> str:
        return getattr(self.provider, "name", "polygon")

    def get_api_stats(self) -> dict:
        stats = self.provider.stats() if hasattr(self.provider, "stats") else {}
        return {
            "cache_entries": len(self.cache),
            "api_calls_made": stats.get("api_calls_made", 0),
            "rate_limit_reached": self.rate_limit_reached,
            "provider": stats.get("provider", self.get_data_mode()),
            "symbol_proxies": stats.get("symbol_proxies", {}),
        }

    def clear_cache(self) -> None:
        self.cache.clear()

    # ------------------------------------------------------------ helpers
    @staticmethod
    def _yf_history(symbol: str, days: int) -> list[dict] | None:
        from scripts.market_data import yf_fallback

        return yf_fallback.daily_history(symbol, days)

    @staticmethod
    def _yf_quote(symbol: str) -> dict | None:
        from scripts.market_data import yf_fallback

        return yf_fallback.quote(symbol)


def _polygon_key(symbol: str) -> str:
    from scripts.market_data.symbols import to_polygon

    try:
        return to_polygon(symbol)[0]
    except (NotAvailable, ValueError):
        return symbol.upper()


def _sma(bars: list[dict], n: int) -> float | None:
    if len(bars) < n:
        return None
    window = bars[-n:]
    return round(sum(b["close"] for b in window) / n, 4)


def today_iso() -> str:
    return date.today().isoformat()
