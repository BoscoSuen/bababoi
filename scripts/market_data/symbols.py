"""Symbol normalisation between FMP/yfinance conventions and Polygon."""

from __future__ import annotations

import re

from scripts.market_data.provider import NotAvailable

# Indices are not on the Polygon Stocks Starter plan → proxy with the tracking ETF.
INDEX_PROXIES = {
    "^GSPC": "SPY",
    "^SPX": "SPY",
    "^IXIC": "QQQ",
    "^NDX": "QQQ",
    "^DJI": "DIA",
    "^RUT": "IWM",
}

# Volatility indices have no ETF proxy with the same level; served by yfinance only.
YFINANCE_ONLY = frozenset({"^VIX", "^VIX3M", "^VIX9D", "^VVIX"})

_CLASS_DASH = re.compile(r"^([A-Z]{1,5})-([A-Z])$")


def to_polygon(symbol: str) -> tuple[str, str | None]:
    """Return ``(polygon_symbol, proxied_from)``.

    - ``BRK-B`` / ``BF-B`` (FMP dash class) → ``BRK.B`` / ``BF.B``
    - ``^GSPC`` → ``SPY`` with ``proxied_from="^GSPC"``
    - raises ``NotAvailable`` for :data:`YFINANCE_ONLY` symbols
    """
    sym = (symbol or "").strip().upper()
    if not sym:
        raise ValueError("empty symbol")
    if sym in YFINANCE_ONLY:
        raise NotAvailable(f"{sym} is not served by Polygon Stocks Starter (indices plan)")
    if sym in INDEX_PROXIES:
        return INDEX_PROXIES[sym], sym
    m = _CLASS_DASH.match(sym)
    if m:
        return f"{m.group(1)}.{m.group(2)}", None
    return sym, None


def to_fmp(symbol: str) -> str:
    """``BRK.B`` → ``BRK-B`` for callers that still key on FMP-style symbols."""
    sym = (symbol or "").strip().upper()
    if re.match(r"^[A-Z]{1,5}\.[A-Z]$", sym):
        return sym.replace(".", "-")
    return sym
