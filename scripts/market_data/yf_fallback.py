"""yfinance fallback for symbols Polygon Starter cannot serve (^VIX, ^VIX3M).

``yfinance`` is optional; every function returns ``None`` when it is missing
or the request fails, so callers degrade instead of crashing.
"""

from __future__ import annotations

try:  # pragma: no cover - exercised via monkeypatch in tests
    import yfinance as _yf

    HAS_YFINANCE = True
except ImportError:  # pragma: no cover
    _yf = None
    HAS_YFINANCE = False


def daily_history(symbol: str, days: int = 260) -> list[dict] | None:
    """Ascending DailyBar rows (adjClose == close) or ``None``."""
    if not HAS_YFINANCE:
        return None
    try:
        hist = _yf.Ticker(symbol).history(period=f"{max(days, 5)}d", auto_adjust=False)
    except Exception:
        return None
    if hist is None or getattr(hist, "empty", True):
        return None
    rows: list[dict] = []
    for idx, row in hist.iterrows():
        try:
            rows.append(
                {
                    "date": idx.strftime("%Y-%m-%d"),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "adjClose": float(row["Close"]),
                    "volume": int(row.get("Volume", 0) or 0),
                    "vwap": None,
                }
            )
        except (KeyError, TypeError, ValueError):
            continue
    return rows[-days:] or None


def quote(symbol: str) -> dict | None:
    """FMP-shaped quote synthesized from ~1y of daily history, or ``None``."""
    rows = daily_history(symbol, 260)
    if not rows:
        return None
    last = rows[-1]
    prev = rows[-2] if len(rows) > 1 else last
    change = last["close"] - prev["close"]
    return {
        "symbol": symbol,
        "price": last["close"],
        "previousClose": prev["close"],
        "change": round(change, 4),
        "changesPercentage": round(change / prev["close"] * 100, 4) if prev["close"] else 0.0,
        "changePercentage": round(change / prev["close"] * 100, 4) if prev["close"] else 0.0,
        "open": last["open"],
        "dayHigh": last["high"],
        "dayLow": last["low"],
        "volume": last["volume"],
        "avgVolume": int(sum(r["volume"] for r in rows) / len(rows)),
        "yearHigh": max(r["high"] for r in rows),
        "yearLow": min(r["low"] for r in rows),
        "marketCap": 0,
        "source": "yfinance",
    }
