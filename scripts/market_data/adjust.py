"""Dividend adjustment for split-adjusted daily bars.

Polygon ``adjusted=true`` aggregates are split-adjusted only. To offer an
FMP-style total-return ``adjClose`` we walk backwards from the newest bar
and multiply a running factor by ``1 - cash_amount / close_before_ex_date``
each time an ex-dividend date is crossed.
"""

from __future__ import annotations

ADJUSTABLE_TYPES = {"CD", "SC", None, ""}  # regular cash + special cash; unknown → adjust


def apply_dividend_adjustment(bars_asc: list[dict], dividends: list[dict]) -> list[dict]:
    """Return a new list (ascending) with ``adjClose`` filled in.

    ``bars_asc``: DailyBar rows sorted ascending by ``date``.
    ``dividends``: rows with ``ex_date`` and ``cash_amount`` (any order).
    Dividends whose ex-date is on/before the first bar are ignored (they
    would scale every bar equally, which changes nothing in-window).
    """
    if not bars_asc:
        return []
    divs = sorted(
        (
            d
            for d in dividends
            if d.get("cash_amount") and d.get("ex_date") and d.get("type") in ADJUSTABLE_TYPES
        ),
        key=lambda d: d["ex_date"],
    )
    out = [dict(bar) for bar in bars_asc]
    factor = 1.0
    j = len(divs) - 1
    for i in range(len(out) - 1, -1, -1):
        bar = out[i]
        # Crossing an ex-date going backwards: the bar *before* the ex-date
        # is the first one that must be scaled down.
        while j >= 0 and divs[j]["ex_date"] > bar["date"]:
            prev_close = float(bar["close"])
            cash = float(divs[j]["cash_amount"])
            if 0 < cash < prev_close:
                factor *= 1.0 - cash / prev_close
            j -= 1
        bar["adjClose"] = round(float(bar["close"]) * factor, 4)
    return out
